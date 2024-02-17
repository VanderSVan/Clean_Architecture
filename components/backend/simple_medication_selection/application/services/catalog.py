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
                 item_reviews_repo: interfaces.ItemReviewsRepo,
                 symptoms_repo: interfaces.SymptomsRepo,
                 diagnoses_repo: interfaces.DiagnosesRepo
                 ) -> None:
        self.items_repo = items_repo
        self.categories_repo = item_categories_repo
        self.types_repo = item_types_repo
        self.reviews_repo = item_reviews_repo
        self.symptoms_repo = symptoms_repo
        self.diagnoses_repo = diagnoses_repo

    @register_method
    @validate_call
    def get_item(self, item_id: int) -> entities.TreatmentItem:
        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id)

        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        return item

    @register_method
    @validate_call
    def search_items(self,
                     keywords: str | None,
                     limit: int = 10,
                     offset: int = 0
                     ) -> list[entities.TreatmentItem] | list[None]:
        return self.items_repo.find_by_keywords(keywords, limit, offset)

    @register_method
    @validate_call
    def find_items_in_rating_range(self,
                                   min_rating: int = 0,
                                   max_rating: int | None = None,
                                   limit: int | None = 10,
                                   offset: int = 0
                                   ) -> list[entities.TreatmentItem] | list[None]:
        return self.reviews_repo.find_in_rating_range(min_rating,
                                                      max_rating,
                                                      limit,
                                                      offset)

    @register_method
    @validate_call
    def find_items_by_helped_status(self,
                                    helped: bool = True,
                                    limit: int | None = 10,
                                    offset: int = 0
                                    ) -> list[entities.TreatmentItem] | list[None]:
        reviews: list[entities.ItemReview] = (
            self.reviews_repo.find_by_helped_status(helped, limit, offset)
        )
        return [review.item for review in reviews]

    @register_method
    @validate_call
    def find_items_by_symptom_and_helped_status(self,
                                                symptom_id: int,
                                                helped: bool = True,
                                                limit: int | None = 10,
                                                offset: int = 0
                                                ) -> list[entities.TreatmentItem]:

        symptom = self.symptoms_repo.fetch_by_id(symptom_id)
        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        reviews: list[entities.ItemReview] = (
            self.reviews_repo.find_by_symptom_id_and_helped_status(symptom_id,
                                                                   helped,
                                                                   limit,
                                                                   offset)
        )
        return [review.item for review in reviews]

    @register_method
    @validate_call
    def find_items_by_diagnosis_and_helped_status(self,
                                                  diagnosis_id: int,
                                                  helped: bool = True,
                                                  limit: int | None = 10,
                                                  offset: int = 0
                                                  ) -> list[entities.TreatmentItem]:

        diagnosis = self.diagnoses_repo.fetch_by_id(diagnosis_id)
        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)

        reviews: list[entities.ItemReview] = (
            self.reviews_repo.find_by_diagnosis_id_and_helped_status(diagnosis_id,
                                                                     helped,
                                                                     limit,
                                                                     offset)
        )
        return [review.item for review in reviews]

    @register_method
    @validate_call
    def find_items_by_category(self,
                               category_id: int,
                               limit: int | None = 10,
                               offset: int = 0
                               ) -> list[entities.TreatmentItem] | list[None]:

        category: entities.ItemCategory = self.categories_repo.fetch_by_id(category_id)
        if not category:
            raise errors.ItemCategoryNotFound(id=category_id)

        return self.items_repo.find_by_category_id(category_id, limit, offset)

    @register_method
    @validate_call
    def find_items_by_type(self,
                           type_id: int,
                           limit: int | None = 10,
                           offset: int = 0
                           ) -> list[entities.TreatmentItem] | list[None]:

        type_: entities.ItemType = self.types_repo.fetch_by_id(type_id)
        if not type_:
            raise errors.ItemTypeNotFound(id=type_id)

        return self.items_repo.find_by_type_id(type_id, limit, offset)

    @register_method
    @validate_call
    def add_item(self,
                 new_item_info: dtos.ItemCreateSchema
                 ) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(new_item_info.id)
        if item:
            raise errors.TreatmentItemAlreadyExists(id=new_item_info.id)

        category: entities.ItemCategory = self.categories_repo.fetch_by_id(
            new_item_info.category_id)
        if not category:
            raise errors.ItemCategoryNotFound(id=new_item_info.category_id)

        type_: entities.ItemType = self.types_repo.fetch_by_id(
            new_item_info.type_id)
        if not type_:
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
    def delete_item(self,
                    item_info: dtos.ItemDeleteSchema
                    ) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_info.id)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_info.id)

        return self.items_repo.remove(item)
