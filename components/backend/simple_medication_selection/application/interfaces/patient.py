from abc import ABC, abstractmethod

from .. import entities


class PatientsRepo(ABC):
    @abstractmethod
    def fetch_by_id(self, patient_id: int) -> entities.Patient | None:
        ...

    @abstractmethod
    def fetch_by_nickname(self, name: str) -> entities.Patient | None:
        ...

    @abstractmethod
    def add(self, patient: entities.Patient) -> entities.Patient:
        ...

    @abstractmethod
    def update(self, patient: entities.Patient) -> entities.Patient:
        ...

    @abstractmethod
    def remove(self, patient: entities.Patient) -> entities.Patient:
        ...
