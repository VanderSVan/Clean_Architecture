from abc import ABC, abstractmethod

from .. import entities


class ItemReviewsRepo(ABC):

    @abstractmethod
    def get_by_id(self, review_id: int) -> entities.ItemReview | None:
        ...

    @abstractmethod
    def get_all(self) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def get_all_by_item_id(self,
                           item_id: int,
                           limit: int | None,
                           offset: int
                           ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_in_rating_range(self,
                             min_rating: int,
                             max_rating: int | None,
                             limit: int | None,
                             offset: int
                             ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_helped_status(self,
                              is_helped: bool,
                              limit: int | None,
                              offset: int
                              ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_symptom_id_and_helped_status(
        self,
        symptom_id: int,
        is_helped: bool,
        limit: int | None,
        offset: int
    ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_diagnosis_id_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        limit: int | None,
        offset: int
    ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        ...

    @abstractmethod
    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        ...
