from typing import Literal

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
                 medical_books_repo: interfaces.MedicalBooksRepo,
                 symptoms_repo: interfaces.SymptomsRepo,
                 diagnoses_repo: interfaces.DiagnosesRepo
                 ) -> None:
        self.items_repo = items_repo
        self.categories_repo = item_categories_repo
        self.types_repo = item_types_repo
        self.reviews_repo = item_reviews_repo
        self.med_books_repo = medical_books_repo
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
    def find_items(self,
                   keywords: str | None = None,
                   *,
                   limit: int = 10,
                   offset: int = 0
                   ) -> list[entities.TreatmentItem] | list[None]:
        if keywords:
            return self.items_repo.fetch_by_keywords(keywords, limit, offset)

        return self.items_repo.fetch_all(limit, offset)

    @register_method
    @validate_call
    def find_items_by_rating(self,
                             min_rating: float = 0,
                             max_rating: float | None = None,
                             *,
                             limit: int | None = 10,
                             offset: int = 0
                             ) -> list[entities.TreatmentItem] | list[None]:
        reviews: list[entities.ItemReview] = (
            self.reviews_repo.fetch_by_rating(min_rating, max_rating, limit, offset)
        )
        return [review.item for review in reviews]

    @register_method
    @validate_call
    def find_items_by_helped_status(self,
                                    is_helped: bool = True,
                                    *,
                                    limit: int | None = 10,
                                    offset: int = 0
                                    ) -> list[entities.TreatmentItem] | list[None]:
        reviews: list[entities.ItemReview] = (
            self.reviews_repo.fetch_by_helped_status(is_helped, limit, offset)
        )
        return [review.item for review in reviews]

    @register_method
    @validate_call
    def find_items_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool = True,
        *,
        order_by_rating: Literal['asc', 'desc'] = 'desc',
        limit: int | None = 10,
        offset: int = 0
    ) -> list[entities.TreatmentItem] | list[None]:
        """
        В данном методе представлен use case, когда
        мы следуем подходу 'smart application, stupid repository'.

        Этот подход имеет очевидные как плюсы, так и минусы:
        + Например, в случае смены db/orm, переписать запрос не составит труда.
        + Не нужно детально описывать, что необходимо получить из db. Следовательно,
        возможная часть бизнес-логики не попадет в репозитории.
        + Не нужно составлять огромные запросы.
        - Но также нужно понимать, что SQL может дать больше возможностей и
        лучше скорость.
        - Нужно хранить лишнюю информацию в памяти.

        Какой подход выбрать решает команда разработки.

        P.S. ниже метод `find_items_by_diagnosis_and_helped_status` как раз следует
        противоположному подходу - 'stupid application, smart repository'.
        """
        med_books: list[entities.MedicalBook] = (
            self.med_books_repo.fetch_by_symptoms(symptom_ids, limit, offset)
        )

        reviews: list[entities.ItemReview] = []
        for med_book in med_books:
            reviews.extend(med_book.item_reviews)

        order = True if order_by_rating == 'desc' else False
        reviews.sort(key=lambda review: review.item_rating, reverse=order)

        return [review.item for review in reviews if review.is_helped == is_helped]

    @register_method
    @validate_call
    def find_items_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool = True,
        *,
        order_by_rating: Literal['asc', 'desc'] = 'desc',
        limit: int | None = 10,
        offset: int = 0
    ) -> list[entities.TreatmentItem] | list[None]:
        """
        В данном методе представлен use case, когда
        мы следуем подходу 'stupid application, smart repository'.

        Этот подход имеет очевидные как плюсы, так и минусы:
        + В памяти не хранится лишняя информация, из db достается уже
        обработанная необходимая информация.
        + Чаще всего SQL предоставляет больше возможностей и лучше скорость.
        - В случае смены db/orm, нам необходимо внимательно переписывать запрос.
        - Необходимо в application более подробно описывать, что мы хотим получить от
        репозитория.
        - Также есть вероятность попадания в репозитории часть бизнес-логики.

        Какой подход выбрать решает команда разработки.

        P.S. выше метод `find_items_by_symptoms_and_helped_status` как раз следует
        противоположному подходу - 'smart application, stupid repository'.
        """
        return self.med_books_repo.fetch_items_by_diagnosis_and_helped_status(
            diagnosis_id, is_helped, order_by_rating, limit, offset
        )

    @register_method
    @validate_call
    def find_items_by_category(self,
                               category_id: int,
                               *,
                               limit: int | None = 10,
                               offset: int = 0
                               ) -> list[entities.TreatmentItem] | list[None]:

        return self.items_repo.fetch_by_category(category_id, limit, offset)

    @register_method
    @validate_call
    def find_items_by_type(self,
                           type_id: int,
                           *,
                           limit: int | None = 10,
                           offset: int = 0
                           ) -> list[entities.TreatmentItem] | list[None]:

        return self.items_repo.fetch_by_type(type_id, limit, offset)

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
    def delete_item(self, item_info: dtos.ItemDeleteSchema) -> entities.TreatmentItem:

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_info.id)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_info.id)

        return self.items_repo.remove(item)
