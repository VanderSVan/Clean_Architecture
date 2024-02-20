from abc import ABC, abstractmethod

from .. import entities


class ItemReviewsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  limit: int,
                  offset: int
                  ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def fetch_all_by_item_id(self,
                             item_id: int,
                             limit: int,
                             offset: int
                             ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def fetch_reviews_by_patient_id(self,
                                    patient_id: int,
                                    limit: int,
                                    offset: int
                                    ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def fetch_patient_reviews_by_item(self,
                                      patient_id: int,
                                      item_id: int,
                                      limit: int,
                                      offset: int
                                      ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def fetch_by_rating(self,
                        min_rating: float,
                        max_rating: float | None,
                        limit: int,
                        offset: int
                        ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(self,
                               is_helped: bool,
                               limit: int,
                               offset: int
                               ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        ...

    @abstractmethod
    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        ...
