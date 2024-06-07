from abc import ABC, abstractmethod
from typing import Sequence

from med_sharing_system.application import entities, schemas


class DiagnosesRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.Diagnosis | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.Diagnosis | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindDiagnoses
                  ) -> Sequence[entities.Diagnosis | None]:
        ...

    @abstractmethod
    def search_by_name(self,
                       filter_params: schemas.FindDiagnoses
                       ) -> Sequence[entities.Diagnosis | None]:
        ...

    @abstractmethod
    def add(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        ...

    @abstractmethod
    def remove(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        ...
