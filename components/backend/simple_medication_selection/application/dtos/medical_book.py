from pydantic import Field

from .base import DTO
from .symptom import Symptom
from .item_review import ItemReviewGetSchema


class MedicalBookCreateSchema(DTO):
    title_history: str = Field(..., min_length=1, max_length=255)
    history: str = Field(None, min_length=1, max_length=5000)
    patient_id: int = Field(..., ge=1)
    diagnosis_id: int = Field(..., ge=1)
    symptoms: list[Symptom] = Field(None)
    item_reviews: list[ItemReviewGetSchema] = Field(None)


class MedicalBookGetSchema(DTO):
    id: int = Field(..., ge=1)
    title_history: str = Field(..., min_length=1, max_length=255)
    history: str = Field(None, min_length=1, max_length=5000)
    patient_id: int = Field(..., ge=1)
    diagnosis_id: int = Field(..., ge=1)


class MedicalBookUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    title_history: str = Field(None, min_length=1, max_length=255)
    history: str = Field(None, min_length=1, max_length=5000)
    patient_id: int = Field(None, ge=1)
    diagnosis_id: int = Field(None, ge=1)
    symptoms: list[Symptom] = Field(None)
    item_reviews: list[ItemReviewGetSchema] = Field(None)
