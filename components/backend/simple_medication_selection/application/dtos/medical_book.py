from typing import Annotated

from pydantic import Field

from .base import DTO
from .symptom import SymptomGetSchema
from .item_review import ItemReviewGetSchema


class MedicalBookCreateSchema(DTO):
    title_history: Annotated[str, Field(min_length=1, max_length=255)]
    history: Annotated[str, Field(min_length=1, max_length=5000)] = Field(None)
    patient_id: Annotated[int, Field(ge=1)]
    diagnosis_id: Annotated[int, Field(ge=1)]
    symptoms: list[SymptomGetSchema] = Field(None)
    item_reviews: list[ItemReviewGetSchema] = Field(None)


class MedicalBookGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    title_history: Annotated[str, Field(min_length=1, max_length=255)]
    history: Annotated[str, Field(min_length=1, max_length=5000)] = Field(None)
    patient_id: Annotated[int, Field(ge=1)]
    diagnosis_id: Annotated[int, Field(ge=1)]


class MedicalBookUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    title_history: Annotated[str, Field(min_length=1, max_length=255)] = Field(None)
    history: Annotated[str, Field(min_length=1, max_length=5000)] = Field(None)
    patient_id: Annotated[int, Field(ge=1)] = Field(None)
    diagnosis_id: Annotated[int, Field(ge=1)] = Field(None)
    symptoms: list[SymptomGetSchema] = Field(None)
    item_reviews: list[ItemReviewGetSchema] = Field(None)
