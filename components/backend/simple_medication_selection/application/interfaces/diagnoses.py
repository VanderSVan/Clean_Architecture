from abc import ABC, abstractmethod

from .. import entities


class DiagnosesRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.Diagnosis | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.Diagnosis | None:
        ...

    @abstractmethod
    def add(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        ...

    @abstractmethod
    def remove(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        ...
