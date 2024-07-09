# Documentation for PyESCAsync

## World Class

### Overview
The `World` class is a central component in an Entity Component System (ECS) architecture. It manages entities, systems, and their interactions.

### Methods

#### `__init__(self)`
Initializes a new `World` instance.

- `next_id`: Counter for entity IDs.
- `entities_map`: Dictionary storing entities and their components.
- `systems`: List of systems with their priorities and parameters.
- `queue`: Priority queue for managing tasks and system calls.
- `event_handlers`: Dictionary for event types and their handlers.
- `tasks`: List to store asyncio tasks.

#### `create_entity(self) -> int`
Creates a new entity and returns its ID.

#### `remove_entity(self, entity: int)`
Schedules the removal of an entity.

#### `get_entities(self)`
Returns a list of all entity IDs.

#### `add_system(self, system: Any, priority: int = 0)`
Adds a system to the world with optional priority.

#### `add_component(self, entity: int, component: Any)`
Adds a component to an entity.

#### `remove_component(self, entity: int, component_type: Type)`
Schedules the removal of a component from an entity.

#### `get_component(self, entity: int, component_type: Type)`
Retrieves a specific component from an entity.

#### `get_components(self, entity: int)`
Returns all components of an entity.

#### `get_entities_with_component(self, component_type: Type)`
Finds all entities with a specified component type.

#### `subscribe(self, event: Type, handler: Callable)`
Subscribes a handler to an event type.

#### `unsubscribe(self, event_type: Type, handler: Callable)`
Unsubscribes a handler from an event type.

#### `event_handler(self, event_type: Type)`
Decorator for event handler functions.

#### `emit(self, event: Any)`
Emits an event and triggers associated handlers.

#### `cleanup_tasks(self)`
Cleans up completed asyncio tasks.

#### `update(self)`
Main loop for processing tasks and system updates.

#### `_update_system(self, system, parameters)`
Updates a single system with relevant entities and components.

#### `run(self)`
Starts the main update loop of the world.

## System Class

### Overview
`System` is an abstract base class for defining systems in the ECS architecture.

### Methods

#### `__init__(self)`
Initializes a new `System` instance.

- `world`: Reference to the `World` instance.

#### `update(self, entity, *args, **kwargs)`
Abstract method that should be implemented in subclasses. It defines the behavior of the system.

### Usage
Subclass `System` and implement the `update` method to define a system's behavior.

### Example

```python
class MySystem(System):
    def update(self, entity, *args, **kwargs):
        # System behavior here
