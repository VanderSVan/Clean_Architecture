from typing import Literal, Sequence

from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
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

    @register_method
    @validate_call
    def get_patient_reviews_by_item(self,
                                    patient_id: int,
                                    item_id: int,
                                    *,
                                    sort_field: Literal[
                                        'id', 'item_id', 'is_helped', 'item_rating',
                                        'item_count', 'usage_period'
                                    ] = 'item_rating',
                                    sort_direction: Literal['asc', 'desc'] = 'desc',
                                    limit: int = 10,
                                    offset: int = 0
                                    ) -> Sequence[entities.ItemReview | None]:

        return self.reviews_repo.fetch_patient_reviews_by_item(patient_id,
                                                               item_id,
                                                               sort_field,
                                                               sort_direction,
                                                               limit,
                                                               offset)

    @register_method
    @validate_call
    def get_reviews_by_item(self,
                            item_id: int,
                            *,
                            sort_field: Literal[
                                'id', 'item_id', 'is_helped', 'item_rating',
                                'item_count', 'usage_period'
                            ] = 'item_rating',
                            sort_direction: Literal['asc', 'desc'] = 'desc',
                            limit: int = 10,
                            offset: int = 0
                            ) -> Sequence[entities.ItemReview | None]:

        return self.reviews_repo.fetch_all_by_item(item_id, sort_field, sort_direction,
                                                   limit, offset)

    @register_method
    @validate_call
    def get_patient_reviews(self,
                            patient_id: int,
                            *,
                            sort_field: Literal[
                                'id', 'item_id', 'is_helped', 'item_rating',
                                'item_count', 'usage_period'
                            ] = 'item_rating',
                            sort_direction: Literal['asc', 'desc'] = 'desc',
                            limit: int = 10,
                            offset: int = 0
                            ) -> Sequence[entities.ItemReview | None]:

        return self.reviews_repo.fetch_reviews_by_patient(patient_id, sort_field,
                                                          sort_direction, limit, offset)

    @register_method
    @validate_call
    def add(self, new_review_info: dtos.ItemReviewCreateSchema) -> entities.ItemReview:
        item: entities.TreatmentItem = self.items_repo.fetch_by_id(
            new_review_info.item_id)
        if not item:
            raise errors.TreatmentItemNotFound(id=new_review_info.item_id)

        new_review: entities.ItemReview = new_review_info.create_obj(entities.ItemReview)
        return self.reviews_repo.add(new_review)

    @register_method
    @validate_call
    def change(self, new_review_info: dtos.ItemReviewUpdateSchema) -> entities.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(new_review_info.id)
        if not review:
            raise errors.ItemReviewNotFound(id=new_review_info.id)

        if new_review_info.item_id:
            item: entities.TreatmentItem = self.items_repo.fetch_by_id(
                new_review_info.item_id
            )
            if not item:
                raise errors.TreatmentItemNotFound(id=new_review_info.item_id)

        return new_review_info.populate_obj(review)

    @register_method
    @validate_call
    def delete(self, review_id: int) -> entities.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(review_id)
        if not review:
            raise errors.ItemReviewNotFound(id=review_id)

        return self.reviews_repo.remove(review)
