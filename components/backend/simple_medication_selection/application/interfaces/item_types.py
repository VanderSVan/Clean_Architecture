from abc import ABC, abstractmethod
from typing import Sequence

from simple_medication_selection.application import entities, schemas


class ItemTypesRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, type_id: int) -> entities.ItemType | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.ItemType | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindItemTypes
                  ) -> Sequence[entities.ItemType | None]:
        ...

    @abstractmethod
    def search_by_name(self,
                       filter_params: schemas.FindItemTypes
                       ) -> Sequence[entities.ItemType | None]:
        ...

    @abstractmethod
    def add(self, item_type: entities.ItemType) -> entities.ItemType:
        ...

    @abstractmethod
    def remove(self, item_type: entities.ItemType) -> entities.ItemType:
        ...
