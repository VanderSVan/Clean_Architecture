from abc import ABC, abstractmethod

from .. import entities


class MedicalBooksRepo(ABC):
    @abstractmethod
    def fetch_by_id(self, med_book_id: int) -> entities.MedicalBook | None:
        ...

    @abstractmethod
    def fetch_by_patient_id(self,
                            patient_id: int,
                            limit: int = 10,
                            offset: int = 0
                            ) -> list[entities.MedicalBook]:
        ...

    @abstractmethod
    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def update(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...
