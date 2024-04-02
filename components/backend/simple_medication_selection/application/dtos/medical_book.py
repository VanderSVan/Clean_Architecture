from pydantic import Field

from .base import DTO
from .symptom import Symptom
from .item_review import ItemReview
from .item_review import ItemReview
from simple_medication_selection.application import entities


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


class NewMedicalBookInfo(DTO):
    title_history: str = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int = Field(ge=1)
    diagnosis_id: int = Field(ge=1)
    symptoms: list[Symptom | None] | None
    item_reviews: list[ItemReview | None] | None


class UpdatedMedicalBookInfo(DTO):
    id: int = Field(ge=1)
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptoms: list[Symptom | None] | None
    item_reviews: list[ItemReview | None] | None
