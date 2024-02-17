from abc import ABC, abstractmethod

from .. import entities


class ItemTypesRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.ItemType | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.ItemType | None:
        ...

    @abstractmethod
    def add(self, item_type: entities.ItemType) -> None:
        ...

    @abstractmethod
    def remove(self, item_type: entities.ItemType) -> None:
        ...
