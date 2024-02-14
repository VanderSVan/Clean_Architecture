from abc import ABC, abstractmethod

from .. import entities


class ItemCategoriesRepo(ABC):

    @abstractmethod
    def get_by_id(self, id_: int) -> entities.ItemCategory | None:
        ...

    @abstractmethod
    def get_by_name(self, name: str) -> entities.ItemCategory | None:
        ...

    @abstractmethod
    def add(self, item_category: entities.ItemCategory) -> None:
        ...

    @abstractmethod
    def remove(self, item_category: entities.ItemCategory) -> None:
        ...
