from typing import Annotated

from pydantic import Field

from .base import DTO
from .item import ItemGetSchema


class ItemReviewCreateSchema(DTO):
    item: Annotated[ItemGetSchema, Field(...)]
    is_helped: Annotated[bool, Field(...)]
    item_rating: Annotated[float, Field(..., ge=1, le=10, multiple_of=0.5)]
    item_count: Annotated[int, Field(..., ge=1)]
    usage_period: Annotated[int, Field(None, ge=1)]


class ItemReviewGetSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    item: Annotated[ItemGetSchema, Field(...)]
    is_helped: Annotated[bool, Field(...)]
    item_rating: Annotated[float, Field(..., ge=1, le=10, multiple_of=0.5)]
    item_count: Annotated[int, Field(..., ge=1)]
    usage_period: Annotated[int, Field(None, ge=1)]


class ItemReviewUpdateSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    item: Annotated[ItemGetSchema, Field(None)]
    is_helped: Annotated[bool, Field(None)]
    item_rating: Annotated[float, Field(None, ge=1, le=10, multiple_of=0.5)]
    item_count: Annotated[int, Field(None, ge=1)]
    usage_period: Annotated[int, Field(None, ge=1)]


class ItemReviewDeleteSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
