from abc import ABC, abstractmethod
from typing import Sequence

from .. import entities, dtos, schemas


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self,
                    item_id: int,
                    include_reviews: bool
                    ) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindTreatmentItems,
                  include_reviews: bool
                  ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_all_with_selected_columns(
        self,
        filter_params: schemas.FindTreatmentItems,
    ) -> list[dtos.TreatmentItem | None]:
        ...

    @abstractmethod
    def update_avg_rating(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...
