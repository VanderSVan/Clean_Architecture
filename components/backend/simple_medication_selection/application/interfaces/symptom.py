from abc import ABC, abstractmethod

from .. import entities


class SymptomsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, id_: int) -> entities.Symptom | None:
        ...

    @abstractmethod
    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        ...

    @abstractmethod
    def add(self, symptom: entities.Symptom) -> entities.Symptom:
        ...

    @abstractmethod
    def remove(self, symptom: entities.Symptom) -> entities.Symptom:
        ...
