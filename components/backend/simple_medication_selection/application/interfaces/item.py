from abc import ABC, abstractmethod
from typing import Sequence

from .. import entities, dtos, schemas


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, item_id: int) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindTreatmentItems,
                  with_reviews: bool
                  ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms_and_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_and_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...
