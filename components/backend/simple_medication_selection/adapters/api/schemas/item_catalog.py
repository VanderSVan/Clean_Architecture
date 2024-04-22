from typing import Literal

from pydantic import BaseModel as BaseSchema, Field


class GetTreatmentItemWithReviews(BaseSchema):
    reviews_sort_field: Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ] | None = None
    reviews_sort_direction: Literal['asc', 'desc'] | None = 'asc'
    reviews_limit: int | None = Field(10, ge=1)
    reviews_offset: int | None = Field(0, ge=0)
