from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemType:
    def __init__(self, types_repo: interfaces.ItemTypesRepo):
        self.types_repo = types_repo

    @register_method
    @validate_call
    def get(self, type_id: int) -> entities.ItemType:

        item_type = self.types_repo.fetch_by_id(type_id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=type_id)

        return item_type

    @register_method
    @validate_call
    def create(self, new_type_info: dtos.ItemTypeCreateSchema) -> entities.ItemType:

        item_type: entities.ItemType = (
            self.types_repo.fetch_by_name(new_type_info.name)
        )
        if item_type:
            raise errors.ItemTypeAlreadyExists(name=new_type_info.name)

        new_type: entities.ItemType = new_type_info.create_obj(entities.ItemType)
        return self.types_repo.add(new_type)

    @register_method
    @validate_call
    def change(self, new_type_info: dtos.ItemTypeUpdateSchema) -> entities.ItemType:

        item_type: entities.ItemType = self.types_repo.fetch_by_id(new_type_info.id)
        if not item_type:
            raise errors.ItemTypeNotFound(id=new_type_info.id)

        if new_type_info.name == item_type.name:
            raise errors.ItemTypeAlreadyExists(name=new_type_info.name)

        return new_type_info.populate_obj(item_type)

    @register_method
    @validate_call
    def delete(self, type_id: int) -> entities.ItemType:

        item_type = self.types_repo.fetch_by_id(type_id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=type_id)

        return self.types_repo.remove(item_type)
