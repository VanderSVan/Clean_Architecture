from simple_medication_selection.application.dtos.base import DTO

from pydantic import Field


class SymptomSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255, example="Повышенная температура")


class SymptomCreateSchema(DTO):
    name: str = Field(..., min_length=1, max_length=255, example="Повышенное давление")


class SymptomUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(None, min_length=1, max_length=255, example="Пониженное давление")
