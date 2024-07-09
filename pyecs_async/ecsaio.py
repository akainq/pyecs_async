import asyncio
import time
import inspect
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Set, Dict, Type, Any, Callable, Tuple, TypeVar
from asyncio.queues import Queue
from pyecs_async.hibitset import HiBitset

_C = TypeVar('_C')


class ECSWorld:
    """
        World is a class that represents the game world

        Example:

            class Position:
                def __init__(self):
                    self.x = 0
                    self.y = 0

            class MovementSystem(System):
                async def update(self, entity, position: Position):
                    position.x += random()
                    position.y += random()

            world = World()
            world.add_system(MovementSystem())
            entity_id = world.create_entity()
            world.add_component(entity_id, Position())


            while True:
                await world.update()
                await asyncio.sleep(1)
    """

    def __init__(self):
        self.next_entity_id:int = 0
        self.entities_map: Dict[int, Dict[Type, _C]] = {}
        self.systems: List[Tuple[int, Callable, Set[_C]]] = []
        self.component_bitsets: Dict[Type, HiBitset] = defaultdict(HiBitset)

        self.queue: Queue = Queue()
        self.event_handlers: Dict[Type, List[Callable]] = {}
        self.tasks: [] = []

    def create_entity(self, *_components: _C) -> int:
        """
        Create entity and return entity id
        """
        entity = self.next_entity_id
        self.entities_map[entity] = {}
        self.next_entity_id +=1

        for component in _components:
            self.add_component(entity, component)

        return entity

    def remove_entity(self, entity: int):
        self.queue.put_nowait(('removeentity', entity))

    def get_entities(self):
        return self.entities_map.keys()

    def add_system(self, system: Any, priority: int = 0):
        system_instance = system
        system = type(system)
        if inspect.isclass(system):
            getmembers = inspect.getmembers(system,
                                            predicate=lambda a: inspect.isfunction(a) and a.__name__ == "update")
            if len(getmembers) == 1:
                update_method = getmembers[0][1]
            else:
                raise ValueError(f"System `{system.__name__}` must have an update method!")
        elif inspect.isfunction(system):
            update_method = system
        else:
            raise ValueError("System must be a class or a function")

        signature = inspect.signature(update_method)
        parameters = {name: param.annotation for name, param in signature.parameters.items() if
                      name not in ("self", "entity")}
        system_instance.world = self
        self.systems.append((priority, system_instance, parameters))
        self.systems.sort(key=lambda system_: system_[0], reverse=False)
        _ = 1
        # self.queue.put_nowait((priority, ('systemcall', (system_instance, parameters))))

    def add_component(self, entity_id: int, component: _C):
        component_type = type(component)
        self.entities_map.setdefault(entity_id, {})[component_type] = component
        self.component_bitsets[component_type].add(entity_id)

    def remove_component(self, entity_id: int, component_type: _C):
        if component_type in self.entities_map.get(entity_id, {}):
            del self.entities_map[entity_id][component_type]
            self.component_bitsets[component_type].remove(entity_id)

    def get_component(self, entity_id: int, component_type: Type):
        if self.component_bitsets[component_type].contains(entity_id):
            return self.entities_map[entity_id].get(component_type)
        return None

    def get_components(self, entity_id: int, *component_types: Type):
        if all(self.component_bitsets[ct].contains(entity_id) for ct in component_types):
            return {ct: self.entities_map[entity_id][ct] for ct in component_types if
                    ct in self.entities_map[entity_id]}
        return None

    def get_components(self, entity_id: int):
        components = {}
        for component_type, bitset in self.component_bitsets.items():
            if bitset.contains(entity_id):
                component = self.entities_map[entity_id].get(component_type)
                if component:
                    components[component_type] = component
        return components

    def get_entities_with_component(self, component_type: _C):
        return [entity for entity, components in self.entities_map.items() if component_type in components]

    def subscribe(self, event: Type, handler: Callable):
        """
        Subscribe to event
        :param event:
        :param handler:
        :return:
        """
        self.event_handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event_type: Type, handler: Callable):
        self.event_handlers[event_type].remove(handler)

    def event_handler(self, event_type: Type):
        """
        Decorator for event handler
        :param event_type:
        :return:
        """

        def decorator(func):
            self.subscribe(event_type, func)
            return func

        return decorator

    async def emit(self, event: Any):
        for handler in self.event_handlers.get(type(event), []):
            loop = asyncio.get_running_loop()
            self.tasks.append(loop.create_task(handler(event)))

    async def cleanup_tasks(self):
        # Очистка завершенных задач
        self.tasks = [task for task in self.tasks if not task.done()]

    async def update(self):
        """
        Update world state and call systems
        """
        start_time = time.time()
        # Lunch systems
        for idx in range(0, len(self.systems)):
            system = self.systems[idx]
            await self._call_system(system[1], system[2])
        # pprint(self.queue)

        # events
        while not self.queue.empty():
            command, system_params = self.queue.get_nowait()
            if command == "removeentity":
                entity = system_params
                if entity in self.entities_map:
                    self.entities_map.pop(entity)
            elif command == "removecomponent":
                entity, component_type = system_params
                self.entities_map[entity].pop(component_type)
            else:
                raise ValueError(f"Unknown task type: {command}")

        await self.cleanup_tasks()
        end_time = time.time()
        # logging.warning(f"Update time: {end_time - start_time}")

    async def _call_system(self, system, parameters):
        required_component_types = parameters.values()
        candidate_entities = set(range(self.next_entity_id))

        for component_type in required_component_types:
            bitset = self.component_bitsets[component_type]
            candidate_entities &= set(idx for idx in range(self.next_entity_id) if bitset.contains(idx))

        for entity in candidate_entities:
            components = self.entities_map.get(entity)
            if components:
                if all(param_type in components for param_type in parameters.values()):
                    kwargs = {param_name: components[param_type] for param_name, param_type in parameters.items()}
                    await system.update(entity, **kwargs)


@dataclass
class System(ABC):
    world: ECSWorld

    def __init__(self):
        self.world = None

    @abstractmethod
    def update(self, entity, *args, **kwargs):
        raise NotImplementedError
