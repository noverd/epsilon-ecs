import unittest
from epsilon_ecs import Entity, Component, component, System, World, Manager


@component
class PositionComponent(Component):
    x: int
    y: int


@component
class VelocityComponent(Component):
    x_speed: int
    y_speed: int


class VelocitySystem(System):
    def stop(self, world: World):
        pass

    def start(self, world: World):
        pass

    def process(self, world: World):
        for uid, entity in world.get_entities_with_component(VelocityComponent):
            velocity = entity.get_component(VelocityComponent)
            position = entity.get_component(PositionComponent)
            position.x += velocity.x_speed * world.get_manager(MulManager).velocity_mul
            position.y += velocity.y_speed * world.get_manager(MulManager).velocity_mul

class MulManager(Manager):
    def init(self, world: World):
        self.velocity_mul: int = 2
        # Some actions with World
        
    def after_init(self, world: World):
        self.velocity_mul: int = 3

    def stop(self, world: World):
        pass
        
class ECS(unittest.TestCase):
    def test_ecs(self):
        world: World = World()
        world.add_manager(MulManager())
        entity: Entity = Entity((PositionComponent(x=0, y=0), VelocityComponent(1, 0)))
        world.add_system(VelocitySystem)
        ent_id: int = world.add_entity(entity)
        world.init()
        world.systems_start()
        for _ in range(10):
            world.systems_process()
        self.assertEqual(world.get_entity(ent_id), entity)
        self.assertEqual(entity.get_component(PositionComponent).x, 30)


if __name__ == '__main__':
    unittest.main()
