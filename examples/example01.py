import asyncio
import time
from dataclasses import dataclass
from random import random
from pyecs_async.ecsaio import System, ECSWorld


@dataclass
class Component1:
    value = -1


@dataclass
class Component2:
    value = -2


@dataclass
class ComponentA:
    value = random()


@dataclass
class ComponentB:
    value = random()

@dataclass
class ComponentC:
    value = random()

@dataclass
class ErrorComponent:
    value = random()


class MyEvent:
    def __init__(self, entity):
        self.entity = entity


class MovementSystem3(System):

    async def update(self, entity, c1: ComponentA, c2: ComponentB, c3: ComponentC, c4: Component1):
        c1.value += random()
        c2.value += random()
        #self.world.remove_entity(entity)
        #print(f"Entity {entity}  from system 3")
        #await self.world.emit(MyEvent(entity))
        #self.world.remove_entity(entity)
        print(f"Entity {entity} for components {c1} {c2} {c3} {c4} from system 3")



class MovementSystem2(System):

    async def update(self, entity, c1: ComponentA, c2: Component2):
        c1.value += random()
        c2.value += random()
        print(f"Entity {entity} for components {c1} {c2} from system 2")

class ErrorSystem(System):

    async def update(self, entity, c1: ErrorComponent):
        c1.value += random()
        print(f"Error component {entity} for components {c1}")
        #await self.world.emit(MyEvent(entity))
        self.world.remove_component(entity, ErrorComponent)


async def main():
    world = ECSWorld()
    world.add_system(ErrorSystem(),0)
    world.add_system(MovementSystem2(),10)
    world.add_system(MovementSystem3(),0)

    @world.event_handler(MyEvent)
    async def test_handler(event: MyEvent):
        print(f"Test handler {event.entity}")


    #time_start = time.time()
    ITER = 1


    time_start = asyncio.get_running_loop().time()
    for i in range(ITER):
        world.create_entity(Component1())

    for i in range(ITER):
        world.create_entity(ComponentA(), Component2(), ErrorComponent())


    for i in range(ITER):
        world.create_entity(ComponentA(), ComponentB(), ComponentC(), Component1(), ErrorComponent())


    await world.update()
    time_end = asyncio.get_running_loop().time()
    #time_end = time.time()
    await asyncio.sleep(1)
    res_time_ms = ((time_end - time_start) * 1000)/ ITER
    print(f"Time: {res_time_ms} ms")


    #for i in range(500):
    #    world.create_entity(ComponentA(), ComponentB())

    #for i in range(500):
    #    world.create_entity(Component1())



if __name__ == '__main__':
    asyncio.run(main())
