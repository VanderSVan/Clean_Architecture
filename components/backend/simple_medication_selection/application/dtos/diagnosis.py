from typing import Annotated

from .base import DTO

from pydantic import Field


class DiagnosisCreateSchema(DTO):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class DiagnosisGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)]


class DiagnosisUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)] = Field(None)


class DiagnosisDeleteSchema(DTO):
    id: Annotated[int, Field(ge=1)]
