from abc import ABC, abstractmethod
from typing import Literal, Sequence

from .. import entities


class MedicalBooksRepo(ABC):
    @abstractmethod
    def fetch_by_id(self, med_book_id: int) -> entities.MedicalBook | None:
        ...

    @abstractmethod
    def fetch_by_patient(self,
                         patient_id: int,
                         limit: int,
                         offset: int
                         ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms(self,
                          symptom_ids: Sequence[int],
                          limit: int,
                          offset: int
                          ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms_and_helped_status(
        self,
        symptom_ids: Sequence[int],
        is_helped: bool,
        limit: int,
        offset: int
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        limit: int,
        offset: int
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...
