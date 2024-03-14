from .base import DTO

from pydantic import Field


class ItemCategoryCreateSchema(DTO):
    name: str = Field(..., min_length=1, max_length=100)


class ItemCategoryGetSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)


class ItemCategoryUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    name: str = Field(None, min_length=1, max_length=100)
