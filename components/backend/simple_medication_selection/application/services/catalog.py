from typing import Literal, Sequence, Optional

from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class TreatmentItemCatalog:
    def __init__(self,
                 items_repo: interfaces.TreatmentItemsRepo,
                 item_categories_repo: interfaces.ItemCategoriesRepo,
                 item_types_repo: interfaces.ItemTypesRepo,
                 ) -> None:
        self.items_repo = items_repo
        self.categories_repo = item_categories_repo
        self.types_repo = item_types_repo

    @register_method
    @validate_call
    def get_item(self, item_id: int) -> entities.TreatmentItem:
        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id)

        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        return item

    @register_method
    @validate_call
    def find_items(self,
                   keywords: str = '',
                   *,
                   sort_field: Literal[
                       'price', 'category_id', 'type_id', 'avg_rating'] = 'avg_rating',
                   sort_direction: Literal['asc', 'desc'] = 'desc',
                   limit: int = 10,
                   offset: int = 0
                   ) -> list[dtos.ItemGetSchema | None]:

        if keywords:
            return self.items_repo.fetch_by_keywords(keywords, sort_field,
                                                     sort_direction, limit, offset)

        return self.items_repo.fetch_all(sort_field, sort_direction, limit, offset)

    @register_method
    @validate_call
    def find_items_with_reviews(self,
                                keywords: str = '',
                                *,
                                sort_field: Literal[
                                    'id', 'title', 'price', 'category_id',
                                    'type_id', 'avg_rating'] = 'avg_rating',
                                sort_direction: Literal['asc', 'desc'] = 'desc',
                                limit: int = 10,
                                offset: int = 0
                                ) -> Sequence[entities.TreatmentItem | None]:

        if keywords:
            return self.items_repo.fetch_by_keywords_with_reviews(keywords, sort_field,
                                                                  sort_direction, limit,
                                                                  offset)

        return self.items_repo.fetch_all_with_reviews(sort_field, sort_direction, limit,
                                                      offset)

    @register_method
    @validate_call
    def find_items_by_category(self,
                               category_id: int,
                               *,
                               sort_field: Literal[
                                   'id', 'title', 'price', 'category_id',
                                   'type_id', 'avg_rating'] = 'avg_rating',
                               sort_direction: Literal['asc', 'desc'] = 'desc',
                               limit: int = 10,
                               offset: int = 0
                               ) -> Sequence[Optional[entities.TreatmentItem]]:

        return self.items_repo.fetch_by_category(category_id, sort_field, sort_direction,
                                                 limit, offset)

    @register_method
    @validate_call
    def find_items_by_type(self,
                           type_id: int,
                           *,
                           sort_field: Literal[
                               'id', 'title', 'price', 'category_id',
                               'type_id', 'avg_rating'] = 'avg_rating',
                           sort_direction: Literal['asc', 'desc'] = 'desc',
                           limit: int = 10,
                           offset: int = 0
                           ) -> Sequence[Optional[entities.TreatmentItem]]:

        return self.items_repo.fetch_by_type(type_id, sort_field, sort_direction, limit,
                                             offset)

    @register_method
    @validate_call
    def find_items_by_rating(self,
                             min_rating: float = 0.0,
                             max_rating: float | None = 10.0,
                             *,
                             sort_field: Literal[
                                 'id', 'title', 'price', 'category_id',
                                 'type_id', 'avg_rating'] = 'avg_rating',
                             sort_direction: Literal['asc', 'desc'] = 'desc',
                             limit: int = 10,
                             offset: int = 0
                             ) -> list[dtos.ItemGetSchema | None]:

        return self.items_repo.fetch_by_rating(min_rating, max_rating, sort_field,
                                               sort_direction, limit, offset)

    @register_method
    @validate_call
    def find_items_by_helped_status(self,
                                    is_helped: bool = True,
                                    *,
                                    sort_field: Literal[
                                        'id', 'title', 'price', 'category_id',
                                        'type_id', 'avg_rating'] = 'avg_rating',
                                    sort_direction: Literal['asc', 'desc'] = 'desc',
                                    limit: int = 10,
                                    offset: int = 0
                                    ) -> list[dtos.ItemWithHelpedStatusGetSchema | None]:

        return self.items_repo.fetch_by_helped_status(is_helped, sort_field,
                                                      sort_direction, limit, offset)

    @register_method
    @validate_call
    def find_items_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool = True,
        *,
        sort_field: Literal[
            'id', 'title', 'price', 'category_id',
            'type_id', 'avg_rating'] = 'avg_rating',
        sort_direction: Literal['asc', 'desc'] = 'desc',
        limit: int = 10,
        offset: int = 0
    ) -> Sequence[Optional[entities.TreatmentItem]]:

        return self.items_repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, is_helped, sort_field, sort_direction, limit, offset
        )

    @register_method
    @validate_call
    def find_items_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool = True,
        *,
        sort_field: Literal[
            'id', 'title', 'price', 'category_id',
            'type_id', 'avg_rating'] = 'avg_rating',
        sort_direction: Literal['asc', 'desc'] = 'desc',
        limit: int = 10,
        offset: int = 0
    ) -> Sequence[Optional[entities.TreatmentItem]]:

        return self.items_repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id, is_helped, sort_field, sort_direction, limit, offset
        )

    @register_method
    @validate_call
    def add_item(self, new_item_info: dtos.ItemCreateSchema) -> entities.TreatmentItem:

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
    @validate_call
    def change_item(self,
                    new_item_info: dtos.ItemUpdateSchema
                    ) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(new_item_info.id)
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
    @validate_call
    def delete_item(self, item_id: int) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        return self.items_repo.remove(item)
