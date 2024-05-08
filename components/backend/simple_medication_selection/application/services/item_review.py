from collections import namedtuple
from typing import Callable, Sequence

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemReview:
    def __init__(self,
                 item_reviews_repo: interfaces.ItemReviewsRepo,
                 items_repo: interfaces.TreatmentItemsRepo
                 ) -> None:
        self.reviews_repo = item_reviews_repo
        self.items_repo = items_repo
        self.search_strategy_selector = _ItemReviewStrategySelector(item_reviews_repo)

    @register_method
    @validate_arguments
    def get_review(self, review_id: int) -> dtos.ItemReview:
        review: entities.ItemReview | None = self.reviews_repo.fetch_by_id(review_id)

        if not review:
            raise errors.ItemReviewNotFound(id=review_id)

        return dtos.ItemReview.from_orm(review)

    @register_method
    @validate_arguments
    def find_reviews(self,
                     filter_params: schemas.FindItemReviews
                     ) -> list[dtos.ItemReview | None]:

        repo_method: Callable = self.search_strategy_selector.get_method(filter_params)

        reviews: Sequence[entities.ItemReview | dtos.ItemReview | None] = (
            repo_method(filter_params)
        )
        if reviews and isinstance(reviews[0], entities.ItemReview):
            return [dtos.ItemReview.from_orm(review) for review in reviews]

        return reviews

    @register_method
    @validate_arguments
    def add(self, new_review_info: dtos.NewItemReviewInfo) -> dtos.ItemReview:
        item: entities.TreatmentItem = self.items_repo.fetch_by_id(
            new_review_info.item_id, False
        )
        if not item:
            raise errors.TreatmentItemNotFound(id=new_review_info.item_id)

        new_review: entities.ItemReview = new_review_info.create_obj(entities.ItemReview)
        added_review: entities.ItemReview = self.reviews_repo.add(new_review)
        self.items_repo.update_avg_rating(item)
        return dtos.ItemReview.from_orm(added_review)

    @register_method
    @validate_arguments
    def change(self, new_review_info: dtos.UpdatedItemReviewInfo) -> dtos.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(new_review_info.id)
        if not review:
            raise errors.ItemReviewNotFound(id=new_review_info.id)

        if new_review_info.item_id:
            item: entities.TreatmentItem = self.items_repo.fetch_by_id(
                new_review_info.item_id, False
            )
            if not item:
                raise errors.TreatmentItemNotFound(id=new_review_info.item_id)

        updated_review: entities.ItemReview = new_review_info.populate_obj(review)

        if new_review_info.item_rating:
            item: entities.TreatmentItem = self.items_repo.fetch_by_id(
                updated_review.item_id, False
            )
            self.items_repo.update_avg_rating(item)

        return dtos.ItemReview.from_orm(updated_review)

    @register_method
    @validate_arguments
    def delete(self, review_id: int) -> dtos.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(review_id)
        if not review:
            raise errors.ItemReviewNotFound(id=review_id)

        removed_review: entities.ItemReview = self.reviews_repo.remove(review)
        return dtos.ItemReview.from_orm(removed_review)


class _ItemReviewStrategySelector:
    """
    Предназначен для выбора стратегии по поиску отзывов пациента.
    Паттерн стратегия.
    """

    def __init__(self, reviews_repo: interfaces.ItemReviewsRepo) -> None:
        self.reviews_repo = reviews_repo
        self.StrategyKey = namedtuple(
            'StrategyKey',
            ['item_ids', 'patient_id', 'is_helped', 'rating']
        )
        self.strategies: dict[namedtuple, Callable] = {
            self.StrategyKey(False, False, False, False): (
                self.reviews_repo.fetch_all
            ),
            self.StrategyKey(True, False, False, False): (
                self.reviews_repo.fetch_by_items
            ),
            self.StrategyKey(False, True, False, False): (
                self.reviews_repo.fetch_by_patient
            ),
            self.StrategyKey(False, False, True, False): (
                self.reviews_repo.fetch_by_helped_status
            ),
            self.StrategyKey(False, False, False, True): (
                self.reviews_repo.fetch_by_rating
            ),
            self.StrategyKey(True, True, False, False): (
                self.reviews_repo.fetch_by_items_and_patient
            ),
            self.StrategyKey(True, False, True, False): (
                self.reviews_repo.fetch_by_items_and_helped_status
            ),
            self.StrategyKey(True, False, False, True): (
                self.reviews_repo.fetch_by_items_and_rating
            ),
            self.StrategyKey(False, True, True, False): (
                self.reviews_repo.fetch_by_patient_and_helped_status
            ),
            self.StrategyKey(False, True, False, True): (
                self.reviews_repo.fetch_by_patient_and_rating
            ),
            self.StrategyKey(False, False, True, True): (
                self.reviews_repo.fetch_by_helped_status_and_rating
            ),
            self.StrategyKey(True, True, True, False): (
                self.reviews_repo.fetch_by_items_patient_and_helped_status
            ),
            self.StrategyKey(True, True, False, True): (
                self.reviews_repo.fetch_by_items_patient_and_rating
            ),
            self.StrategyKey(True, False, True, True): (
                self.reviews_repo.fetch_by_items_helped_status_and_rating
            ),
            self.StrategyKey(False, True, True, True): (
                self.reviews_repo.fetch_by_patient_helped_status_and_rating
            ),
            self.StrategyKey(True, True, True, True): (
                self.reviews_repo.fetch_by_items_patient_helped_status_and_rating
            )
        }

    def _build_key(self, filter_params: schemas.FindItemReviews) -> namedtuple:
        return self.StrategyKey(
            item_ids=True if filter_params.item_ids is not None else False,
            patient_id=True if filter_params.patient_id is not None else False,
            is_helped=True if filter_params.is_helped is not None else False,
            rating=any((filter_params.min_rating is not None,
                        filter_params.max_rating is not None))
        )

    def get_method(self, filter_params: schemas.FindItemReviews) -> Callable:
        key: namedtuple = self._build_key(filter_params)
        return self.strategies[key]
