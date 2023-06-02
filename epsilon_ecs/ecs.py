from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Set, TypeVar, get_args

hashing_dataclass = dataclass(slots=True, unsafe_hash=True)  # Base component decorator

TC = TypeVar("TC")


class Component(object):
    pass


class Entity:
    """
    Base entity class for all entities.
    """

    def __init__(self, components: Set[Component] = None):
        """
        :param components: Set of components for entity
        """
        if isinstance(components, set):
            self.components: Set[Component] = components
        else:
            self.components: Set[Component] = set()

    def __repr__(self) -> str:
        return f"Entity(components={self.components})"

    def __str__(self) -> str:
        return f"Entity(components={self.components})"

    def add_component(self, component: Component) -> None:
        """
        Adding component to self.components
        :param component: Component to add
        :return: None
        """
        self.components.add(component)

    def get_component(self, component_type: TC) -> TC | None:
        """
        Searches for a component by component_type
        :type component_type: Component children
        :param component_type: Type of component
        :return: Component or None if there is no such component
        """
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp

    def remove_component(self, component_type: TC) -> bool:
        """
        Searching and removing a component from self.components
        :param component_type: Type of component
        :return: True if the component is found and removed, False otherwise
        """
        for comp in self.components:
            if isinstance(comp, component_type):
                self.components.remove(comp)
                return True
        return False

    def has_component(self, component_type: type) -> bool:
        return any(isinstance(comp, component_type) for comp in self.components)


class System(ABC):

    @abstractmethod
    def start(self, world: "World"):
        """
        Called when the systems_start method is called on World
        :param world: ECS-World object
        :return:
        """
        pass

    @abstractmethod
    def process(self, world: "World"):
        """
        Called when the systems_process method is called on World
        :param world: ECS-World object
        :return:
        """
        pass

    @abstractmethod
    def stop(self, world: "World"):
        """
        Called when the systems_stop method is called on World
        :param world: ECS-World object
        :return:
        """
        pass


class World:
    _uid_counter: int = 0

    def __init__(self):
        self.entities: Dict[int, Entity] = {}
        self.systems: Set[System] = set()

    def add_entity(self, entity: Entity) -> int:
        self._uid_counter += 1
        self.entities[self._uid_counter] = entity
        return self._uid_counter

    def get_entity(self, entity_uid: int) -> Entity | None:
        return self.entities.get(entity_uid)

    def get_entities_with_component(self, component_type: type) -> tuple[tuple[int, Entity]]:
        return tuple((uid, entity) for uid, entity in self.entities.items() if entity.has_component(component_type))

    def add_system(self, system: System) -> None:
        self.systems.add(system)

    def systems_start(self) -> None:
        for sys in self.systems:
            sys.start(sys, world=self)

    def systems_process(self) -> None:
        for sys in self.systems:
            sys.process(sys, world=self)

    def systems_stop(self) -> None:
        for sys in self.systems:
            sys.stop(sys, world=self)
