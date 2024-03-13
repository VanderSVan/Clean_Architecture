from typing import Annotated

from .base import DTO

from pydantic import Field


class ItemCategoryCreateSchema(DTO):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class ItemCategoryGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)]


class ItemCategoryUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)] = Field(None)
