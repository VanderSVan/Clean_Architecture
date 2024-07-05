from abc import ABC, abstractmethod
from typing import Sequence

from med_sharing_system.application import entities, schemas


class ItemReviewsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindItemReviews,
                  ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items(self,
                       filter_params: schemas.FindItemReviews,
                       ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_patient(self,
                         filter_params: schemas.FindItemReviews,
                         ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_patient_reviews_by_item(self,
                                      filter_params: schemas.FindItemReviews,
                                      ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_rating(self,
                        filter_params: schemas.FindItemReviews,
                        ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(self,
                               filter_params: schemas.FindItemReviews,
                               ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_patient(self,
                                   filter_params: schemas.FindItemReviews,
                                   ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_helped_status(self,
                                         filter_params: schemas.FindItemReviews,
                                         ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_rating(self,
                                  filter_params: schemas.FindItemReviews,
                                  ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_helped_status(self,
                                           filter_params: schemas.FindItemReviews,
                                           ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_rating(self,
                                    filter_params: schemas.FindItemReviews,
                                    ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_and_rating(self,
                                          filter_params: schemas.FindItemReviews,
                                          ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_patient_and_helped_status(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_patient_and_rating(self,
                                          filter_params: schemas.FindItemReviews,
                                          ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_helped_status_and_rating(self,
                                                filter_params: schemas.FindItemReviews,
                                                ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def fetch_by_items_patient_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | None]:
        ...

    @abstractmethod
    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        ...

    @abstractmethod
    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        ...
