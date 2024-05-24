from pydantic import Field, validator, root_validator

from simple_medication_selection.application import errors
from .base import DTO
from .item_review import ItemReview
from .symptom import Symptom


class MedicalBook(DTO):
    id: int = Field(ge=1)
    title_history: str = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int = Field(ge=1)
    diagnosis_id: int = Field(ge=1)

    def __hash__(self):
        return hash((self.id, self.patient_id, self.diagnosis_id))

    def __eq__(self, other):
        if not isinstance(other, MedicalBook):
            return False

        return (self.id == other.id and
                self.patient_id == other.patient_id and
                self.diagnosis_id == other.diagnosis_id)

    class Config:
        orm_mode = True


class MedicalBookWithSymptoms(MedicalBook):
    symptoms: list[Symptom | None]


class MedicalBookWithItemReviews(MedicalBook):
    item_reviews: list[ItemReview | None]


class MedicalBookWithSymptomsAndItemReviews(MedicalBookWithSymptoms,
                                            MedicalBookWithItemReviews):
    pass


class NewMedicalBookInfo(DTO):
    title_history: str = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int = Field(ge=1)
    diagnosis_id: int = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    item_review_ids: list[int] | None = Field(ge=1)

    @validator('symptom_ids', pre=True)
    def make_symptoms_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @validator('item_review_ids', pre=True)
    def make_item_reviews_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value


class MedicalBookInfoToUpdate(DTO):
    id: int = Field(ge=1)
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids_to_add: list[int] | None = Field(ge=1)
    item_review_ids_to_add: list[int] | None = Field(ge=1)
    symptom_ids_to_remove: list[int] | None = Field(ge=1)
    item_review_ids_to_remove: list[int] | None = Field(ge=1)

    @validator('symptom_ids_to_add', pre=True)
    def make_symptoms_to_add_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @validator('item_review_ids_to_add', pre=True)
    def make_item_reviews_to_add_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @validator('symptom_ids_to_remove', pre=True)
    def make_symptoms_to_remove_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @validator('item_review_ids_to_remove', pre=True)
    def make_item_reviews_to_remove_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @root_validator
    def fix_symptoms(cls, values) -> dict:
        symptom_ids_to_add: list[int] | None = values.get('symptom_ids_to_add')
        symptom_ids_to_remove: list[int] | None = values.get('symptom_ids_to_remove')

        if not all((symptom_ids_to_add, symptom_ids_to_remove)):
            return values

        intersection: set[int | None] = (
            set(symptom_ids_to_add) & set(symptom_ids_to_remove)
        )
        if intersection:
            raise errors.MedicalBookSymptomsIntersection(
                symptom_ids_to_add=values['symptom_ids_to_add'],
                symptom_ids_to_remove=values['symptom_ids_to_remove']
            )

        return values

    @root_validator
    def fix_item_reviews(cls, values) -> dict:
        item_review_ids_to_add: list[int] | None = values.get('item_review_ids_to_add')
        item_review_ids_to_remove: list[int] | None = (
            values.get('item_review_ids_to_remove')
        )

        if not all((item_review_ids_to_add, item_review_ids_to_remove)):
            return values

        intersection: set[int | None] = (
            set(item_review_ids_to_add) & set(item_review_ids_to_remove)
        )
        if intersection:
            raise errors.MedicalBookReviewsIntersection(
                item_review_ids_to_add=values['item_review_ids_to_add'],
                item_review_ids_to_remove=values['item_review_ids_to_remove']
            )

        return values


class UpdatedMedicalBookInfo(DTO):
    id: int = Field(ge=1)
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    item_review_ids: list[int] | None = Field(ge=1)

    @validator('symptom_ids', pre=True)
    def make_symptoms_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value

    @validator('item_review_ids', pre=True)
    def make_item_reviews_unique(cls, value) -> list[int] | None:
        if isinstance(value, list):
            return list(set(value))
        return value
