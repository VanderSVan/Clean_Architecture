from typing import Sequence

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class TreatmentItemCatalog:
    def __init__(self,
                 items_repo: interfaces.TreatmentItemsRepo,
                 item_reviews_repo: interfaces.ItemReviewsRepo,
                 item_categories_repo: interfaces.ItemCategoriesRepo,
                 item_types_repo: interfaces.ItemTypesRepo,
                 ) -> None:
        self.items_repo = items_repo
        self.reviews_repo = item_reviews_repo
        self.categories_repo = item_categories_repo
        self.types_repo = item_types_repo

    @register_method
    @validate_arguments
    def get_item(self, filter_params: schemas.GetTreatmentItem) -> dtos.TreatmentItem:
        item: entities.TreatmentItem | None = (
            self.items_repo.fetch_by_id(filter_params.item_id, False)
        )

        if not item:
            raise errors.TreatmentItemNotFound(id=filter_params.item_id)

        return dtos.TreatmentItem.from_orm(item)

    @register_method
    @validate_arguments
    def get_item_with_reviews(self,
                              filter_params: schemas.GetTreatmentItemWithReviews
                              ) -> dtos.TreatmentItemWithReviews:
        include_all_reviews: bool = not (
            filter_params.reviews_limit or
            filter_params.reviews_offset or
            filter_params.reviews_sort_field or
            filter_params.exclude_review_fields
        )
        item: entities.TreatmentItem | None = (
            self.items_repo.fetch_by_id(filter_params.item_id, include_all_reviews)
        )
        if not item:
            raise errors.TreatmentItemNotFound(id=filter_params.item_id)

        if include_all_reviews:
            return dtos.TreatmentItemWithReviews.from_orm(item)

        item_info = dtos.TreatmentItem.from_orm(item)
        review_filter_params = schemas.FindItemReviews(
            item_ids=[item_info.id],
            sort_field=filter_params.reviews_sort_field,
            sort_direction=filter_params.reviews_sort_direction,
            limit=filter_params.reviews_limit,
            offset=filter_params.reviews_offset,
            exclude_review_fields=filter_params.exclude_review_fields
        )
        reviews: Sequence[entities.ItemReview] = (
            self.reviews_repo.fetch_by_items(review_filter_params)
        )
        return dtos.TreatmentItemWithReviews(**item_info.dict(), reviews=reviews)

    @register_method
    @validate_arguments
    def find_items(self,
                   filter_params: schemas.FindTreatmentItems
                   ) -> list[dtos.TreatmentItem | None]:

        if filter_params.exclude_item_fields:
            return self.items_repo.fetch_all_with_selected_columns(filter_params)

        items: Sequence[entities.TreatmentItem | None] = (
            self.items_repo.fetch_all(filter_params, False)
        )
        return [dtos.TreatmentItem.from_orm(item) for item in items]

    @register_method
    @validate_arguments
    def find_items_with_reviews(self,
                                filter_params: schemas.FindTreatmentItemsWithReviews
                                ) -> list[dtos.TreatmentItemWithReviews | None]:
        items_with_selected_fields: bool = (
            True if filter_params.exclude_item_fields else False
        )
        reviews_filter_params: bool = (
            True if any(
                [filter_params.reviews_sort_field,
                 filter_params.reviews_sort_direction,
                 filter_params.reviews_limit,
                 filter_params.reviews_offset,
                 filter_params.exclude_review_fields]
            ) else False
        )

        if not items_with_selected_fields and not reviews_filter_params:
            return self._get_items_with_reviews(filter_params)

        if not items_with_selected_fields:
            items_without_reviews: list[dtos.TreatmentItem | None] = (
                self._get_only_items(filter_params)
            )
            return self._add_reviews_to_items(items_without_reviews, filter_params)

        items_without_reviews: list[dtos.TreatmentItem | None] = (
            self._get_only_items_with_selected_fields(filter_params)
        )
        return self._add_reviews_to_items(items_without_reviews, filter_params)

    @register_method
    @validate_arguments
    def add_item(self,
                 new_item_info: dtos.NewTreatmentItemInfo
                 ) -> dtos.TreatmentItemWithReviews:

        category: entities.ItemCategory = self.categories_repo.fetch_by_id(
            new_item_info.category_id)
        if not category:
            raise errors.ItemCategoryNotFound(id=new_item_info.category_id)

        item_type: entities.ItemType = self.types_repo.fetch_by_id(
            new_item_info.type_id)
        if not item_type:
            raise errors.ItemTypeNotFound(id=new_item_info.type_id)

        new_item: entities.TreatmentItem = new_item_info.create_obj(
            entities.TreatmentItem)

        added_item: entities.TreatmentItem = self.items_repo.add(new_item)
        return dtos.TreatmentItemWithReviews.from_orm(added_item)

    @register_method
    @validate_arguments
    def change_item(self,
                    new_item_info: dtos.UpdatedTreatmentItemInfo
                    ) -> dtos.TreatmentItemWithReviews:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(new_item_info.id, True)
        if not item:
            raise errors.TreatmentItemNotFound(id=new_item_info.id)

        if new_item_info.category_id:
            category: entities.ItemCategory = (
                self.categories_repo.fetch_by_id(new_item_info.category_id)
            )
            if not category:
                raise errors.ItemCategoryNotFound(id=new_item_info.category_id)

        if new_item_info.type_id:
            type_: entities.ItemType = self.types_repo.fetch_by_id(new_item_info.type_id)
            if not type_:
                raise errors.ItemTypeNotFound(id=new_item_info.type_id)

        updated_item: entities.TreatmentItem = new_item_info.populate_obj(item)
        return dtos.TreatmentItemWithReviews.from_orm(updated_item)

    @register_method
    @validate_arguments
    def delete_item(self, item_id: int) -> dtos.TreatmentItemWithReviews:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id, True)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        removed_item: entities.TreatmentItem = self.items_repo.remove(item)
        return dtos.TreatmentItemWithReviews.from_orm(removed_item)

    def _get_items_with_reviews(self,
                                filter_params: schemas.FindTreatmentItemsWithReviews
                                ) -> list[dtos.TreatmentItemWithReviews | None]:
        items: Sequence[entities.TreatmentItem | None] = (
            self.items_repo.fetch_all(filter_params, True)
        )
        return [dtos.TreatmentItemWithReviews.from_orm(item) for item in items]

    def _get_only_items(self,
                        filter_params: schemas.FindTreatmentItemsWithReviews
                        ) -> list[dtos.TreatmentItem | None]:
        items: Sequence[entities.TreatmentItem | None] = (
            self.items_repo.fetch_all(filter_params, False)
        )
        return [dtos.TreatmentItem.from_orm(item) for item in items]

    def _get_only_items_with_selected_fields(
        self,
        filter_params: schemas.FindTreatmentItemsWithReviews
    ) -> list[dtos.TreatmentItem | None]:

        return self.items_repo.fetch_all_with_selected_columns(filter_params)

    def _add_reviews_to_items(self,
                              items: list[dtos.TreatmentItem],
                              filter_params: schemas.FindTreatmentItemsWithReviews
                              ) -> list[dtos.TreatmentItemWithReviews | None]:

        items_with_reviews: list[dtos.TreatmentItemWithReviews] = []
        for item in items:
            review_filter_params: schemas.FindItemReviews = (
                schemas.FindItemReviews(
                    item_ids=[item.id],
                    sort_field=filter_params.reviews_sort_field,
                    sort_direction=filter_params.reviews_sort_direction,
                    limit=filter_params.reviews_limit,
                    offset=filter_params.reviews_offset,
                    exclude_review_fields=filter_params.exclude_review_fields
                )
            )
            reviews: Sequence[entities.ItemReview | dtos.ItemReview | None] = (
                self.reviews_repo.fetch_by_items(review_filter_params)
            )
            if reviews and isinstance(reviews[0], entities.ItemReview):
                reviews = [dtos.ItemReview.from_orm(review) for review in reviews]

            items_with_reviews.append(
                dtos.TreatmentItemWithReviews(**item.dict(), reviews=reviews)
            )
        return items_with_reviews
