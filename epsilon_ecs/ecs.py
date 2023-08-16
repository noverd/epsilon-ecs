from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, Future

component = dataclass(slots=True)


@component
class Component:
    owner: Optional["Entity"] = field(default=None, init=False)
    deleted: bool = field(default=False, init=False)

class Entity:
    """
    Base entity class for all entities.
    """

    def __init__(self, components: Optional[Iterable[Component]] = None, owner: Optional["Entity"] = None):
        """
        :param components: Iterable collection of components for entity
        """
        self.components: list[Component] = [] if components is None else [*components]
        self.owner: Optional["Entity"] = owner
        self.deleted: bool = False

    def __repr__(self) -> str:
        return f"Entity(components={self.components}, owner={self.owner}, deleted={self.deleted})"

    def __str__(self) -> str:
        return self.__repr__()

    def add_component(self, component: Component) -> None:
        """
        Adding component to self.components
        :param component: Component to add
        :return: None
        """
        if component.deleted:
            raise ValueError(f"Component {component} is deleted")
        elif component.owner is not None:
            raise ValueError(f"Component {component} is aleardy added to entity")
        component.owner = self
        self.components.append(component)

    def get_component[TC: Component](self, component_type: TC) -> Optional[TC]:
        """
        Searches for a component by component_type
        :type component_type: Component children
        :param component_type: Type of component
        :return: Component or None if there is no such component
        """
        for comp in self.components:
            if isinstance(comp, component_type):
                return comp

    def remove_component[TC: Component](self, component_type: TC) -> bool:
        """
        Searching and removing a component from self.components
        :param component_type: Type of component
        :return: True if the component is found and removed, False otherwise
        """
        for x, comp in enumerate(self.components):
            if isinstance(comp, component_type):
                self.components[x].deleted = True
                del self.components[x]
                return True
        return False

    def has_component[TC: Component](self, component_type: TC) -> bool:
        return any(isinstance(comp, component_type) for comp in self.components)
    
    def delete_entity(self) -> None:
    	for component in self.components:
    	    component.deleted = True
    	self.deleted = True


class System(ABC):

    @abstractmethod
    def start(self, world: "World") -> None:
        """
        Called when the systems_start method is called on World
        :param world: ECS-World object
        :return:
        """
        pass

    @abstractmethod
    def process(self, world: "World") -> None:
        """
        Called when the systems_process method is called on World
        :param world: ECS-World object
        :return:
        """
        pass

    @abstractmethod
    def stop(self, world: "World") -> None:
        """
        Called when the systems_stop method is called on World
        :param world: ECS-World object
        :return:
        """
        pass

class Manager(ABC):
    dependencies: tuple["Manager"] = ()
    @abstractmethod
    def init(world: "World") -> None:
        """
        Called when the init_managers method is called on World
        :param world: ECS-World object
        :return:
        """
        pass
    @abstractmethod
    def after_init(world: "World") -> None:
        """
        Called after when the init method is called on World
        :param world: ECS-World object
        :return:
        """
        pass
    
    @abstractmethod
    def stop(world: "World") -> None:
        """
        Called after when the stop_systems method is called on World
        :param world: ECS-World object
        :return:
        """
        pass



class World:
    _uid_counter: int = 0
    managers: list[Manager]

    def __init__(self, workers_count: int = 2) -> None:
        """
        :param workers_count: Count of the workers for ECS-Systems and Managers work
        :return:
        """
        self.entities: dict[int, Entity] = dict()
        self.systems: list[System] = list()
        self.workers_count: int = workers_count
        self.inited: bool = False
        self.managers: set = set()

    def init(self) -> None:
        """
        Initialize managers
        :return:
        """
        for manager in self.managers:
            manager.init(self)
        for manager in self.managers:
            for dep in manager.dependencies:
                if not dep in self.managers:
                    raise ValueError(f"Required manager {dep} for {manager} but not given.")
        for manager in self.managers:
            manager.after_init(self)
        self.inited = True

    def add_entity(self, entity: Entity) -> int:
        self._uid_counter += 1
        self.entities[self._uid_counter] = entity
        return self._uid_counter

    def get_entity(self, entity_uid: int) -> Optional[Entity]:
        return self.entities.get(entity_uid)

    def get_entities_with_component(self, component_type: type) -> tuple[tuple[int, Entity]]:
        return tuple((uid, entity) for uid, entity in self.entities.items() if entity.has_component(component_type))
    
    def get_manager[MT: Manager](self, manager_type: MT) -> Optional[MT]:
        for manager in self.managers:
            if type(manager) is manager_type:
                return manager

    def add_system(self, system: System) -> None:
    	for sys in self.systems:
    		if isinstance(sys)
        self.systems.append(system)

    def add_systems(self, systems: Iterable[System]) -> None:
        for sys in systems:
            self.systems.append(sys)

    def add_manager(self, manager: Manager) -> None:
        if self.inited:
            raise ValueError("You can't add new manager because World is inited.")
        self.managers.add(manager)

    def systems_start(self) -> None:
        with ThreadPoolExecutor(max_workers=self.workers_count) as ex:
            futures: set[Future] = set()
            for sys in self.systems:
                futures.add(ex.submit(sys.start, sys, world=self))
            for future in futures:
                future.result()

    def systems_process(self) -> None:
        with ThreadPoolExecutor(max_workers=self.workers_count) as ex:
            futures: set[Future] = set()
            for sys in self.systems:
                futures.add(ex.submit(sys.process, sys, world=self))
            for future in futures:
                future.result()

    def systems_stop(self) -> None:
        with ThreadPoolExecutor(max_workers=self.workers_count) as ex:
            futures: set[Future] = set()
            for sys in self.systems:
                futures.add(ex.submit(sys.stop, sys, world=self))
            for future in futures:
                future.result()
