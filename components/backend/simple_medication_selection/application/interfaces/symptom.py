from abc import ABC, abstractmethod
from typing import Sequence, Literal

from .. import entities


class SymptomsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.Symptom | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  order_field: str,
                  order_direction: Literal['asc', 'desc'],
                  limit: int | None,
                  offset: int | None
                  ) -> Sequence[entities.Symptom]:
        ...

    @abstractmethod
    def search_by_name(self,
                       name: str,
                       order_field: str,
                       order_direction: Literal['asc', 'desc'],
                       limit: int | None,
                       offset: int | None
                       ) -> Sequence[entities.Symptom | None]:
        ...

    @abstractmethod
    def add(self, symptom: entities.Symptom) -> entities.Symptom:
        ...

    @abstractmethod
    def remove(self, symptom: entities.Symptom) -> entities.Symptom:
        ...
