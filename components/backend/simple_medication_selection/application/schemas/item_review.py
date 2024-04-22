from typing import Literal

from pydantic import BaseModel as BaseSchema, Field


class FindItemReviews(BaseSchema):
    item_ids: list[int] | None = Field(ge=1)
    is_helped: bool | None
    min_rating: float | None = Field(ge=0, le=10)
    max_rating: float | None = Field(ge=1, le=10)
    sort_field: Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ] | None = 'item_rating'
    sort_direction: Literal['asc', 'desc'] | None = 'desc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)

