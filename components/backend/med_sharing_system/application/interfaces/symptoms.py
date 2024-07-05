from abc import ABC, abstractmethod
from typing import Sequence

from .. import entities, schemas


class SymptomsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.Symptom | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindSymptoms
                  ) -> Sequence[entities.Symptom]:
        ...

    @abstractmethod
    def search_by_name(self,
                       filter_params: schemas.FindSymptoms
                       ) -> Sequence[entities.Symptom | None]:
        ...

    @abstractmethod
    def add(self, symptom: entities.Symptom) -> entities.Symptom:
        ...

    @abstractmethod
    def remove(self, symptom: entities.Symptom) -> entities.Symptom:
        ...
