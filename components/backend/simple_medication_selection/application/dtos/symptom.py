from .base import DTO

from pydantic import Field


class SymptomCreateSchema(DTO):
    name: str = Field(..., min_length=1, max_length=100)


class SymptomGetSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)


class SymptomUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)
