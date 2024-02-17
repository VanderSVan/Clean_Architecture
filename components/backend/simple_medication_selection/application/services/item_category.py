from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemCategory:
    def __init__(self, categories_repo: interfaces.ItemCategoriesRepo):
        self.categories_repo = categories_repo

    @register_method
    @validate_call
    def get(self, item_category_id: int) -> entities.ItemCategory:
        category = self.categories_repo.fetch_by_id(item_category_id)

        if not category:
            raise errors.ItemCategoryNotFound(id=item_category_id)

        return category

    @register_method
    @validate_call
    def create(self, new_item_category_info: dtos.ItemCategoryCreateSchema) -> None:
        category: entities.ItemCategory = (
            self.categories_repo.fetch_by_name(new_item_category_info.name)
        )

        if category:
            raise errors.ItemCategoryAlreadyExists(name=new_item_category_info.name)

        new_item_category: entities.ItemCategory = (
            new_item_category_info.create_obj(entities.ItemCategory)
        )
        self.categories_repo.add(new_item_category)

    @register_method
    @validate_call
    def update(self, new_item_category_info: dtos.ItemCategoryUpdateSchema) -> None:
        category: entities.ItemCategory = (
            self.categories_repo.fetch_by_id(new_item_category_info.id)
        )
        if not category:
            raise errors.ItemCategoryNotFound(id=new_item_category_info.id)

        if new_item_category_info.name == category.name:
            raise errors.ItemCategoryAlreadyExists(name=new_item_category_info.name)

        new_item_category_info.populate_obj(category)

    @register_method
    @validate_call
    def delete(self, item_category_info: dtos.ItemCategoryDeleteSchema) -> None:
        category = self.categories_repo.fetch_by_id(item_category_info.id)

        if not category:
            raise errors.ItemCategoryNotFound(id=item_category_info.id)

        self.categories_repo.remove(category)
