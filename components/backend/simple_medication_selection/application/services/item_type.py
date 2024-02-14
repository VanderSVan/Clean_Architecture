from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemType:
    def __init__(self, item_types_repo: interfaces.ItemTypesRepo):
        self.item_types_repo = item_types_repo

    @register_method
    @validate_call
    def get(self, item_type_id: int) -> entities.ItemType:
        item_type = self.item_types_repo.get_by_id(item_type_id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=item_type_id)

        return item_type

    @register_method
    @validate_call
    def create(self, new_item_type_info: dtos.ItemTypeCreateSchema) -> None:
        item_type: entities.ItemType = self.item_types_repo.get_by_name(new_item_type_info.name)

        if item_type:
            raise errors.ItemTypeAlreadyExists(name=new_item_type_info.name)

        new_item_type: entities.ItemType = new_item_type_info.create_obj(entities.ItemType)
        self.item_types_repo.add(new_item_type)

    @register_method
    @validate_call
    def update(self, new_item_type_info: dtos.ItemTypeUpdateSchema) -> None:
        item_type: entities.ItemType = self.item_types_repo.get_by_id(new_item_type_info.id)
        if not item_type:
            raise errors.ItemTypeNotFound(id=new_item_type_info.id)

        if new_item_type_info.name == item_type.name:
            raise errors.ItemTypeAlreadyExists(name=new_item_type_info.name)

        new_item_type_info.populate_obj(item_type)

    @register_method
    @validate_call
    def delete(self, item_type_info: dtos.ItemTypeDeleteSchema) -> None:
        item_type = self.item_types_repo.get_by_id(item_type_info.id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=item_type_info.id)

        self.item_types_repo.remove(item_type)
