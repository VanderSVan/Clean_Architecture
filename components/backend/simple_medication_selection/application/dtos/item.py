from decimal import Decimal
from typing import Annotated

from pydantic import Field

from .base import DTO


class ItemCreateSchema(DTO):
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: int = Annotated[int, Field(..., ge=1)]
    type_id: int = Annotated[int, Field(..., ge=1)]


class ItemGetSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: Annotated[int, Field(..., ge=1)]
    type_id: Annotated[int, Field(..., ge=1)]


class ItemUpdateSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    title: Annotated[str, Field(None, min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: Annotated[int, Field(None, ge=1)]
    type_id: Annotated[int, Field(None, ge=1)]


class ItemDeleteSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
