from .base import DTO

from pydantic import Field


class DiagnosisCreateSchema(DTO):
    name: str = Field(..., min_length=1, max_length=100)


class DiagnosisGetSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)


class DiagnosisUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(None, min_length=1, max_length=100)
