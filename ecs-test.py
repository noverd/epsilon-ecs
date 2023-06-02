import unittest
from epsilon_ecs import Entity, Component, hashing_dataclass, System, World


@hashing_dataclass
class PositionComponent(Component):
    x: int
    y: int


@hashing_dataclass
class VelocityComponent(Component):
    x_speed: int
    y_speed: int


class VelocitySystem(System):
    def stop(self, world: "World"):
        pass

    def start(self, world: "World"):
        pass

    def process(self, world: World):
        for uid, entity in world.get_entities_with_component(VelocityComponent):
            velocity = entity.get_component(VelocityComponent)
            position = entity.get_component(PositionComponent)
            position.x += velocity.x_speed
            position.y += velocity.y_speed


class ECS(unittest.TestCase):
    def test_something(self):
        world = World()
        entity: Entity = Entity({PositionComponent(x=0, y=0), VelocityComponent(1, 0)})
        world.add_system(VelocitySystem)
        ent_id = world.add_entity(entity)
        world.systems_start()
        for _ in range(10):
            world.systems_process()
        self.assertEqual(world.get_entity(ent_id), entity)
        self.assertEqual(entity.get_component(PositionComponent).x, 10)


if __name__ == '__main__':
    unittest.main()
