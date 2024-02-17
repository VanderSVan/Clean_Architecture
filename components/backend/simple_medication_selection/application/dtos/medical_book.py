from typing import Annotated

from pydantic import Field

from .base import DTO
from .symptom import SymptomGetSchema
from .item_review import ItemReviewGetSchema


class MedicalBookCreateSchema(DTO):
    title_history: Annotated[str, Field(..., min_length=1, max_length=255)]
    history: Annotated[str, Field(None, min_length=1, max_length=5000)]
    patient_id: Annotated[int, Field(..., ge=1)]
    diagnosis_id: Annotated[int, Field(..., ge=1)]
    symptoms: Annotated[list[SymptomGetSchema], Field(None)]
    item_reviews: Annotated[list[ItemReviewGetSchema], Field(None)]


class MedicalBookGetSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    title_history: Annotated[str, Field(..., min_length=1, max_length=255)]
    history: Annotated[str, Field(None, min_length=1, max_length=5000)]
    patient_id: Annotated[int, Field(..., ge=1)]
    diagnosis_id: Annotated[int, Field(..., ge=1)]
    symptoms: Annotated[list[SymptomGetSchema], Field(None)]
    item_reviews: Annotated[list[ItemReviewGetSchema], Field(None)]


class MedicalBookUpdateSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    title_history: Annotated[str, Field(None, min_length=1, max_length=255)]
    history: Annotated[str, Field(None, min_length=1, max_length=5000)]
    patient_id: Annotated[int, Field(None, ge=1)]
    diagnosis_id: Annotated[int, Field(None, ge=1)]
    symptoms: Annotated[list[SymptomGetSchema], Field(None)]
    item_reviews: Annotated[list[ItemReviewGetSchema], Field(None)]


class MedicalBookDeleteSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
