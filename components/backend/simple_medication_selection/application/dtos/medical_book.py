from pydantic import Field

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
    id: int | None = Field(ge=1)
    title_history: str = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int = Field(ge=1)
    diagnosis_id: int = Field(ge=1)
    symptom_ids_to_add: list[int] | None
    item_review_ids_to_add: list[int] | None
    symptom_ids_to_remove: list[int] | None
    item_review_ids_to_remove: list[int] | None


class UpdatedMedicalBookInfo(DTO):
    id: int = Field(ge=1)
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None
    item_review_ids: list[int] | None
