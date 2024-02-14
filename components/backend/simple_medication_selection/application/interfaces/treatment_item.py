from abc import ABC, abstractmethod

from .. import entities


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def get_by_code(self, code: str) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def add(self, treatment_item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def remove(self, treatment_item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...
