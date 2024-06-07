from typing import Sequence

from pydantic import validate_arguments

from med_sharing_system.application import (
    dtos, entities, interfaces, errors, schemas
)
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemCategory:
    def __init__(self, categories_repo: interfaces.ItemCategoriesRepo):
        self.categories_repo = categories_repo

    @register_method
    @validate_arguments
    def get(self, category_id: int) -> dtos.ItemCategory:
        category = self.categories_repo.fetch_by_id(category_id)

        if not category:
            raise errors.ItemCategoryNotFound(id=category_id)

        return dtos.ItemCategory.from_orm(category)

    @register_method
    @validate_arguments
    def find(self,
             filter_params: schemas.FindItemCategories
             ) -> list[dtos.Diagnosis | None]:

        if filter_params.keywords:
            categories: Sequence[entities.Diagnosis | None] = (
                self.categories_repo.search_by_name(filter_params)
            )
            return [dtos.Diagnosis.from_orm(diagnosis) for diagnosis in categories]

        categories: Sequence[entities.Diagnosis | None] = (
            self.categories_repo.fetch_all(filter_params)
        )
        return [dtos.Diagnosis.from_orm(diagnosis) for diagnosis in categories]

    @register_method
    @validate_arguments
    def add(self, new_category_info: dtos.NewItemCategoryInfo) -> dtos.ItemCategory:

        category: entities.ItemCategory = (
            self.categories_repo.fetch_by_name(new_category_info.name)
        )
        if category:
            raise errors.ItemCategoryAlreadyExists(name=new_category_info.name)

        new_item_category: entities.ItemCategory = (
            new_category_info.create_obj(entities.ItemCategory)
        )
        added_category: entities.ItemCategory = (
            self.categories_repo.add(new_item_category)
        )
        return dtos.ItemCategory.from_orm(added_category)

    @register_method
    @validate_arguments
    def change(self, new_category_info: dtos.ItemCategory) -> dtos.ItemCategory:

        category: entities.ItemCategory = (
            self.categories_repo.fetch_by_id(new_category_info.id)
        )
        if not category:
            raise errors.ItemCategoryNotFound(id=new_category_info.id)

        category_with_same_name: entities.ItemCategory | None = (
            self.categories_repo.fetch_by_name(new_category_info.name)
        )
        if category_with_same_name and category_with_same_name.id != category.id:
            raise errors.ItemCategoryAlreadyExists(name=new_category_info.name)

        updated_category: entities.ItemCategory = new_category_info.populate_obj(category)
        return dtos.ItemCategory.from_orm(updated_category)

    @register_method
    @validate_arguments
    def delete(self, category_id: int) -> dtos.ItemCategory:

        category = self.categories_repo.fetch_by_id(category_id)

        if not category:
            raise errors.ItemCategoryNotFound(id=category_id)

        removed_category: entities.ItemCategory = self.categories_repo.remove(category)
        return dtos.ItemCategory.from_orm(removed_category)
