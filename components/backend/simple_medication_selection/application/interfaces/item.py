from abc import ABC, abstractmethod
from typing import Sequence, Literal

from .. import entities, dtos


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, item_id: int) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  order_field: str | None,
                  order_direction: Literal['asc', 'desc'] | None,
                  limit: int | None,
                  offset: int | None
                  ) -> list[dtos.ItemGetSchema | None]:
        ...

    @abstractmethod
    def fetch_all_with_reviews(self,
                               order_field: str | None,
                               order_direction: Literal['asc', 'desc'] | None,
                               limit: int | None,
                               offset: int | None
                               ) -> Sequence[entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_keywords(self,
                          keywords: str,
                          order_field: str | None,
                          order_direction: Literal['asc', 'desc'] | None,
                          limit: int | None,
                          offset: int
                          ) -> list[dtos.ItemGetSchema | None]:
        ...

    @abstractmethod
    def fetch_by_keywords_with_reviews(self,
                                       keywords: str,
                                       order_field: str | None,
                                       order_direction: Literal['asc', 'desc'] | None,
                                       limit: int | None,
                                       offset: int
                                       ) -> Sequence[entities.TreatmentItem | None]:
        ...

    @abstractmethod
    def fetch_by_category(self,
                          category_id: int,
                          order_field: str,
                          order_direction: Literal['asc', 'desc'],
                          limit: int | None,
                          offset: int
                          ) -> list[dtos.ItemGetSchema | None]:
        ...

    @abstractmethod
    def fetch_by_type(self,
                      type_id: int,
                      order_field: str,
                      order_direction: Literal['asc', 'desc'],
                      limit: int | None,
                      offset: int
                      ) -> list[dtos.ItemGetSchema | None]:
        ...

    @abstractmethod
    def fetch_by_rating(self,
                        min_rating: float,
                        max_rating: float,
                        order_field: str,
                        order_direction: Literal['asc', 'desc'],
                        limit: int | None,
                        offset: int | None
                        ) -> list[dtos.ItemGetSchema | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(
        self,
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusGetSchema | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusSymptomsGetSchema | None]:
        ...

    def fetch_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusDiagnosisGetSchema | None]:
        ...

    @abstractmethod
    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...
