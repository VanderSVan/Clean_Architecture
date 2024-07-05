from typing import Sequence

from pydantic import validate_arguments

from med_sharing_system.application import (
    dtos, entities, interfaces, errors, schemas
)
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemType:
    def __init__(self, types_repo: interfaces.ItemTypesRepo):
        self.types_repo = types_repo

    @register_method
    @validate_arguments
    def get(self, type_id: int) -> dtos.ItemType:

        item_type: entities.ItemType | None = self.types_repo.fetch_by_id(type_id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=type_id)

        return dtos.ItemType.from_orm(item_type)
    
    @register_method
    @validate_arguments
    def find(self,
             filter_params: schemas.FindItemTypes
             ) -> list[dtos.ItemType | None]:

        if filter_params.keywords:
            types: Sequence[entities.ItemType | None] = (
                self.types_repo.search_by_name(filter_params)
            )
            return [dtos.ItemType.from_orm(item_type) for item_type in types]

        types: Sequence[entities.ItemType | None] = (
            self.types_repo.fetch_all(filter_params)
        )
        return [dtos.ItemType.from_orm(item_type) for item_type in types]

    @register_method
    @validate_arguments
    def add(self, new_type_info: dtos.NewItemTypeInfo) -> dtos.ItemType:

        item_type: entities.ItemType = (
            self.types_repo.fetch_by_name(new_type_info.name)
        )
        if item_type:
            raise errors.ItemTypeAlreadyExists(name=new_type_info.name)

        new_type: entities.ItemType = new_type_info.create_obj(entities.ItemType)
        added_type: entities.ItemType = self.types_repo.add(new_type)
        return dtos.ItemType.from_orm(added_type)

    @register_method
    @validate_arguments
    def change(self, new_type_info: dtos.ItemType) -> dtos.ItemType:

        item_type: entities.ItemType = self.types_repo.fetch_by_id(new_type_info.id)
        if not item_type:
            raise errors.ItemTypeNotFound(id=new_type_info.id)

        item_type_with_same_name = self.types_repo.fetch_by_name(new_type_info.name)
        if item_type_with_same_name and item_type_with_same_name.id != new_type_info.id:
            raise errors.ItemTypeAlreadyExists(name=new_type_info.name)

        updated_type: entities.ItemType = new_type_info.populate_obj(item_type)
        return dtos.ItemType.from_orm(updated_type)

    @register_method
    @validate_arguments
    def delete(self, type_id: int) -> dtos.ItemType:

        item_type = self.types_repo.fetch_by_id(type_id)

        if not item_type:
            raise errors.ItemTypeNotFound(id=type_id)

        removed_type: entities.ItemType = self.types_repo.remove(item_type)
        return dtos.ItemType.from_orm(removed_type)
