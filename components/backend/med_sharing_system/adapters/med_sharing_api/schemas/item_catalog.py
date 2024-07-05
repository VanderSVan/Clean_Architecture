from decimal import Decimal
from typing import Literal

from pydantic import BaseModel as BaseSchema, Field


class GetTreatmentItemWithReviews(BaseSchema):
    reviews_sort_field: Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ] | None = None
    reviews_sort_direction: Literal['asc', 'desc'] | None = 'asc'
    reviews_limit: int | None = Field(10, ge=1)
    reviews_offset: int | None = Field(0, ge=0)
    exclude_review_fields: list[Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ]] | None = None


class PutTreatmentItemInfo(BaseSchema):
    title: str | None = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int | None = Field(ge=1)
    type_id: int | None = Field(ge=1)
