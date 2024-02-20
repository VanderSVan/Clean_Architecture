from abc import ABC, abstractmethod
from typing import Literal

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
                         ) -> list[entities.MedicalBook] | list[None]:
        ...

    def fetch_by_symptoms(self,
                          symptom_ids: list[int],
                          limit: int,
                          offset: int
                          ) -> list[entities.MedicalBook] | list[None]:
        ...

    def fetch_items_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool,
        order_by_rating: Literal['asc', 'desc'],
        limit: int,
        offset: int
    ) -> list[entities.TreatmentItem] | list[None]:
        ...

    def fetch_items_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        order_by_rating: Literal['asc', 'desc'],
        limit: int,
        offset: int
    ) -> list[entities.MedicalBook] | list[None]:
        ...

    @abstractmethod
    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...
