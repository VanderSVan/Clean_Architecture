from collections import namedtuple
from typing import Sequence, Callable

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class _ItemSearchStrategySelector:
    """
    Предназначен для выбора стратегии по поиску элементов лечения.
    """

    def __init__(self, items_repo: interfaces.TreatmentItemsRepo) -> None:
        self.items_repo = items_repo
        self.StrategyKey = namedtuple(
            'StrategyKey',
            ['diagnosis_id', 'symptom_ids', 'is_helped']
        )
        self.strategies: dict[namedtuple, Callable] = {
            self.StrategyKey(diagnosis_id=True, symptom_ids=True, is_helped=True): (
                self.items_repo.fetch_by_helped_status_diagnosis_symptoms
            ),
            self.StrategyKey(diagnosis_id=True, symptom_ids=True, is_helped=False): (
                self.items_repo.fetch_by_diagnosis_and_symptoms
            ),
            self.StrategyKey(diagnosis_id=True, symptom_ids=False, is_helped=True): (
                self.items_repo.fetch_by_diagnosis_and_helped_status
            ),
            self.StrategyKey(diagnosis_id=True, symptom_ids=False, is_helped=False): (
                self.items_repo.fetch_by_diagnosis
            ),
            self.StrategyKey(diagnosis_id=False, symptom_ids=True, is_helped=True): (
                self.items_repo.fetch_by_symptoms_and_helped_status
            ),
            self.StrategyKey(diagnosis_id=False, symptom_ids=True, is_helped=False): (
                self.items_repo.fetch_by_symptoms
            ),
            self.StrategyKey(diagnosis_id=False, symptom_ids=False, is_helped=True): (
                self.items_repo.fetch_by_helped_status
            ),
            self.StrategyKey(diagnosis_id=False, symptom_ids=False, is_helped=False): (
                self.items_repo.fetch_all
            )
        }

    def _build_key(self, filter_params: schemas.FindTreatmentItemList) -> namedtuple:
        return self.StrategyKey(
            True if filter_params.diagnosis_id is not None else False,
            True if filter_params.symptom_ids is not None else False,
            True if filter_params.is_helped is not None else False
        )

    def get_method(self, filter_params: schemas.FindTreatmentItemList) -> Callable:
        key: namedtuple = self._build_key(filter_params)
        return self.strategies.get(key)


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
        self._search_strategy_selector = _ItemSearchStrategySelector(self.items_repo)

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
                              filter_params: schemas.GetTreatmentItem
                              ) -> dtos.TreatmentItemWithReviews:
        with_reviews: bool = not (
            filter_params.reviews_limit or
            filter_params.reviews_offset or
            filter_params.reviews_sort_field
        )
        item: entities.TreatmentItem | None = (
            self.items_repo.fetch_by_id(filter_params.item_id, with_reviews)
        )
        if not item:
            raise errors.TreatmentItemNotFound(id=filter_params.item_id)

        if with_reviews:
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

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        result: Sequence[entities.TreatmentItem | None] = (
            repo_method(filter_params, False)
        )
        return [dtos.TreatmentItem.from_orm(row) for row in result]

    @register_method
    @validate_arguments
    def find_items_with_reviews(self,
                                filter_params: schemas.FindTreatmentItemList
                                ) -> Sequence[entities.TreatmentItem | None]:

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        result: Sequence[entities.TreatmentItem | None] = (
            repo_method(filter_params, True)
        )
        return [dtos.TreatmentItemWithReviews.from_orm(row) for row in result]

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
