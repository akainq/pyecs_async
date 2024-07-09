import asyncio
import unittest
from pyecs_async import ECSWorld, System  # Replace 'your_module' with the actual name of your module


class TestWorld(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.world = ECSWorld()

    async def test_entity_creation_removal(self):
        entity_id = self.world.create_entity()
        self.assertIn(entity_id, self.world.get_entities())
        self.world.remove_entity(entity_id)
        await self.world.update()
        await asyncio.sleep(0.1)  # Allow time for the entity to be removed
        self.assertNotIn(entity_id, self.world.get_entities())

    async def test_add_remove_component(self):
        entity_id = self.world.create_entity()
        component = "TestComponent"  # Replace with a real component
        self.world.add_component(entity_id, component)
        self.assertEqual(self.world.get_component(entity_id, type(component)), component)
        self.world.remove_component(entity_id, type(component))
        await self.world.update()
        await asyncio.sleep(1)
        self.assertIsNone(self.world.get_component(entity_id, type(component)))

    async def test_system_update(self):

        class TestComponent:
            def __init__(self):
                self.value = 0

        class MockSystem(System):
            async def update(self, entity, test_component: TestComponent):
                test_component.value += 1

        mock_system = MockSystem()
        self.world.add_system(mock_system)
        entity_id = self.world.create_entity()
        self.world.add_component(entity_id, TestComponent())
        await self.world.update()
        await asyncio.sleep(1)
        # Verify that the system update had the expected effect
        self.assertEqual(self.world.get_component(entity_id, TestComponent).value, 1)


    async def test_event_handling(self):
        event_handled = asyncio.Event()

        class TestEvent:
            pass

        @self.world.event_handler(TestEvent)
        async def handle_test_event(event):
            event_handled.set()

        await self.world.emit(TestEvent())
        await event_handled.wait()
        self.assertTrue(event_handled.is_set())

    async def test_cleanup_tasks(self):
        self.world.tasks.append(asyncio.create_task(asyncio.sleep(0.1)))
        await asyncio.sleep(0.2)  # Allow the task to complete
        await self.world.cleanup_tasks()
        self.assertEqual(len(self.world.tasks), 0)


if __name__ == '__main__':
    unittest.main()
