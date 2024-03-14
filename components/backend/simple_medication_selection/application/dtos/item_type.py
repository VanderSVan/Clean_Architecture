from .base import DTO

from pydantic import Field


class ItemTypeCreateSchema(DTO):
    name: str = Field(..., min_length=1, max_length=100)


class ItemTypeGetSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)


class ItemTypeUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(None, min_length=1, max_length=100)
