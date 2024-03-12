from abc import ABC, abstractmethod
from typing import Sequence, Literal

from .. import entities


class ItemReviewsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  order_field: str,
                  order_direction: Literal['asc', 'desc'],
                  limit: int,
                  offset: int
                  ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_all_by_item(self,
                          item_id: int,
                          order_field: str,
                          order_direction: Literal['asc', 'desc'],
                          limit: int,
                          offset: int
                          ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_reviews_by_patient(self,
                                 patient_id: int,
                                 order_field: str,
                                 order_direction: Literal['asc', 'desc'],
                                 limit: int,
                                 offset: int
                                 ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_patient_reviews_by_item(self,
                                      patient_id: int,
                                      item_id: int,
                                      order_field: str,
                                      order_direction: Literal['asc', 'desc'],
                                      limit: int,
                                      offset: int
                                      ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_rating(self,
                        min_rating: float,
                        max_rating: float | None,
                        order_field: str,
                        order_direction: Literal['asc', 'desc'],
                        limit: int,
                        offset: int
                        ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(self,
                               is_helped: bool,
                               order_field: str,
                               order_direction: Literal['asc', 'desc'],
                               limit: int,
                               offset: int
                               ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        ...

    @abstractmethod
    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        ...
