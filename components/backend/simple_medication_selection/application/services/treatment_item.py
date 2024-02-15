from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class TreatmentItem:
    def __init__(self,
                 treatment_items_repo: interfaces.TreatmentItemsRepo,
                 item_categories_repo: interfaces.ItemCategoriesRepo,
                 item_types_repo: interfaces.ItemTypesRepo
                 ) -> None:
        self.treatment_items_repo = treatment_items_repo
        self.item_categories_repo = item_categories_repo
        self.item_types_repo = item_types_repo

    @register_method
    @validate_call
    def get(self, treatment_item_code: str) -> entities.TreatmentItem:
        treatment_item: entities.TreatmentItem = self.treatment_items_repo.get_by_code(treatment_item_code)

        if not treatment_item:
            raise errors.TreatmentItemNotFound(code=treatment_item_code)

        return treatment_item

    @register_method
    @validate_call
    def create(self, new_treatment_item_info: dtos.TreatmentItemCreateSchema) -> entities.TreatmentItem:
        treatment_item: entities.TreatmentItem = self.treatment_items_repo.get_by_code(new_treatment_item_info.code)
        if treatment_item:
            raise errors.TreatmentItemAlreadyExists(code=new_treatment_item_info.code)

        item_category: entities.ItemCategory = self.item_categories_repo.get_by_id(new_treatment_item_info.category_id)
        if not item_category:
            raise errors.ItemCategoryNotFound(id=new_treatment_item_info.category_id)

        item_type: entities.ItemType = self.item_types_repo.get_by_id(new_treatment_item_info.type_id)
        if not item_type:
            raise errors.ItemTypeNotFound(id=new_treatment_item_info.type_id)

        new_treatment_item: entities.TreatmentItem = new_treatment_item_info.create_obj(entities.TreatmentItem)
        return self.treatment_items_repo.add(new_treatment_item)

    @register_method
    @validate_call
    def update(self, new_treatment_item_info: dtos.TreatmentItemUpdateSchema) -> entities.TreatmentItem:
        treatment_item: entities.TreatmentItem = self.treatment_items_repo.get_by_code(new_treatment_item_info.code)
        if not treatment_item:
            raise errors.TreatmentItemNotFound(code=new_treatment_item_info.code)

        if new_treatment_item_info.category_id:
            item_category: entities.ItemCategory = (
                self.item_categories_repo.get_by_id(new_treatment_item_info.category_id)
            )
            if not item_category:
                raise errors.ItemCategoryNotFound(id=new_treatment_item_info.category_id)

        if new_treatment_item_info.type_id:
            item_type: entities.ItemType = self.item_types_repo.get_by_id(new_treatment_item_info.type_id)
            if not item_type:
                raise errors.ItemTypeNotFound(id=new_treatment_item_info.type_id)

        return new_treatment_item_info.populate_obj(treatment_item)

    @register_method
    @validate_call
    def delete(self, treatment_item_info: dtos.TreatmentItemDeleteSchema) -> entities.TreatmentItem:
        treatment_item: entities.TreatmentItem = self.treatment_items_repo.get_by_code(treatment_item_info.code)
        if not treatment_item:
            raise errors.TreatmentItemNotFound(code=treatment_item_info.code)

        return self.treatment_items_repo.remove(treatment_item)
