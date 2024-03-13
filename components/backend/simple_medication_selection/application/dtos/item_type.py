from typing import Annotated

from .base import DTO

from pydantic import Field


class ItemTypeCreateSchema(DTO):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class ItemTypeGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)]


class ItemTypeUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1, max_length=100)] = Field(None)


class ItemTypeDeleteSchema(DTO):
    id: Annotated[int, Field(ge=1)]
