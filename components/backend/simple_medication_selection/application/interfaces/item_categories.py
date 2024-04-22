from abc import ABC, abstractmethod

from .. import entities


class ItemCategoriesRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, category_id: int) -> entities.ItemCategory | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.ItemCategory | None:
        ...

    @abstractmethod
    def add(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        ...

    @abstractmethod
    def remove(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        ...
