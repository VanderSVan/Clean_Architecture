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
    def find_in_rating_range(self,
                             min_rating: int,
                             max_rating: int | None,
                             limit: int,
                             offset: int
                             ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_helped_status(self,
                              is_helped: bool,
                              limit: int,
                              offset: int
                              ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_symptom_id_and_helped_status(
        self,
        symptom_id: int,
        is_helped: bool,
        limit: int,
        offset: int
    ) -> list[entities.ItemReview] | list[None]:
        ...

    @abstractmethod
    def find_by_diagnosis_id_and_helped_status(
        self,
        diagnosis_id: int,
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
