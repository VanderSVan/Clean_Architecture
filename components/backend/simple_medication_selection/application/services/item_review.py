from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class ItemReviews:
    def __init__(self,
                 item_reviews_repo: interfaces.ItemReviewsRepo,
                 items_repo: interfaces.TreatmentItemsRepo,
                 medical_books_repo: interfaces.MedicalBooksRepo,
                 patients_repo: interfaces.PatientsRepo
                 ) -> None:
        self.reviews_repo = item_reviews_repo
        self.items_repo = items_repo
        self.med_books_repo = medical_books_repo
        self.patients_repo = patients_repo

    @register_method
    @validate_call
    def get_patient_review_by_item(self,
                                   patient_id: int,
                                   item_id: int,
                                   limit: int = 10,
                                   offset: int = 0
                                   ) -> list[entities.ItemReview] | list[None]:

        patient: entities.Patient = self.patients_repo.fetch_by_id(patient_id)
        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(item_id)
        if not item:
            raise errors.TreatmentItemNotFound(id=item_id)

        return self.reviews_repo.fetch_patient_reviews_by_item(patient_id,
                                                               item_id,                                                               
                                                               limit,
                                                               offset)

    @register_method
    @validate_call
    def get_item_reviews(self,
                         item_id: int,
                         limit: int,
                         offset: int
                         ) -> list[entities.ItemReview] | list[None]:
        return self.reviews_repo.fetch_all_by_item_id(item_id, limit, offset)

    @register_method
    @validate_call
    def get_patient_reviews(self,
                            patient_id: int
                            ) -> list[entities.ItemReview] | list[None]:
        patient: entities.Patient = self.patients_repo.fetch_by_id(patient_id)
        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        return self.reviews_repo.fetch_reviews_by_patient_id(patient_id)

    @register_method
    @validate_call
    def add(self, new_review_info: dtos.ItemReviewCreateSchema) -> entities.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(new_review_info.id)
        if review:
            raise errors.ItemReviewAlreadyExists(id=new_review_info.id)

        item: entities.TreatmentItem = self.items_repo.fetch_by_id(
            new_review_info.item.id)
        if not item:
            raise errors.TreatmentItemNotFound(id=new_review_info.item.id)

        new_review: entities.ItemReview = new_review_info.create_obj(entities.ItemReview)
        return self.reviews_repo.add(new_review)

    @register_method
    @validate_call
    def change(self, new_review_info: dtos.ItemReviewUpdateSchema) -> entities.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(new_review_info.id)
        if not review:
            raise errors.ItemReviewNotFound(id=new_review_info.id)

        if new_review_info.item:
            item: entities.TreatmentItem = self.items_repo.fetch_by_id(
                new_review_info.item.id
            )
            if not item:
                raise errors.TreatmentItemNotFound(id=new_review_info.item.id)

        return new_review_info.populate_obj(review)

    @register_method
    @validate_call
    def delete(self, review_info: dtos.ItemReviewDeleteSchema) -> entities.ItemReview:
        review: entities.ItemReview = self.reviews_repo.fetch_by_id(review_info.id)
        if not review:
            raise errors.ItemReviewNotFound(id=review_info.id)

        return self.reviews_repo.remove(review)
