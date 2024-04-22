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
            filter_params.reviews_sort_field
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
            offset=filter_params.reviews_offset
        )
        reviews: Sequence[entities.ItemReview] = (
            self.reviews_repo.fetch_by_item(review_filter_params)
        )
        return dtos.TreatmentItemWithReviews(**item_info.dict(), reviews=reviews)

    @register_method
    @validate_arguments
    def find_items(self,
                   filter_params: schemas.FindTreatmentItemList
                   ) -> list[dtos.TreatmentItem | None]:

        result: Sequence[entities.TreatmentItem | None] = (
            self.items_repo.fetch_all(filter_params, False)
        )
        return [dtos.TreatmentItem.from_orm(row) for row in result]

    @register_method
    @validate_arguments
    def find_items_with_reviews(self,
                                filter_params: schemas.FindTreatmentItemListWithReviews
                                ) -> list[dtos.TreatmentItemWithReviews | None]:

        include_all_reviews: bool = not (
            filter_params.reviews_limit or
            filter_params.reviews_offset or
            filter_params.reviews_sort_field
        )

        result: Sequence[entities.TreatmentItem | None] = (
            self.items_repo.fetch_all(filter_params, include_all_reviews)
        )

        if include_all_reviews:
            return [dtos.TreatmentItemWithReviews.from_orm(item) for item in result]

        items_with_limited_reviews: list[dtos.TreatmentItemWithReviews] = []
        for item in result:
            item_info = dtos.TreatmentItem.from_orm(item)
            review_filter_params = schemas.FindItemReviews(
                item_ids=[item_info.id],
                sort_field=filter_params.reviews_sort_field,
                sort_direction=filter_params.reviews_sort_direction,
                limit=filter_params.reviews_limit,
                offset=filter_params.reviews_offset
            )
            reviews: Sequence[entities.ItemReview] = (
                self.reviews_repo.fetch_by_item(review_filter_params)
            )
            items_with_limited_reviews.append(
                dtos.TreatmentItemWithReviews(**item_info.dict(), reviews=reviews)
            )

        return items_with_limited_reviews

    @register_method
    @validate_arguments
    def add_item(self,
                 new_item_info: dtos.NewTreatmentItemInfo) -> entities.TreatmentItem:

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

        return self.items_repo.add(new_item)

    @register_method
    @validate_arguments
    def change_item(self,
                    new_item_info: dtos.UpdatedTreatmentItemInfo
                    ) -> entities.TreatmentItem:

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

        return new_item_info.populate_obj(item)

    @register_method
    @validate_arguments
    def delete_item(self, item_id: int) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id, True)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        return self.items_repo.remove(item)
