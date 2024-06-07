from typing import Literal

from pydantic import BaseModel as BaseSchema, Field, validator

from med_sharing_system.application import dtos, errors


class FindItemReviews(BaseSchema):
    item_ids: list[int] | None = Field(ge=1)
    patient_id: int | None = Field(ge=1)
    is_helped: bool | None
    min_rating: float | None = Field(ge=0, le=10)
    max_rating: float | None = Field(ge=1, le=10)
    sort_field: Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ] | None = 'item_rating'
    sort_direction: Literal['asc', 'desc'] | None = 'desc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)
    exclude_review_fields: list[Literal[
        'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ]] | None = None

    @validator('item_ids', pre=True)
    def fix_item_ids(cls, value):
        if value is not None and not isinstance(value, list):
            return list(value)

        if isinstance(value, list):
            return set(value)

        return value

    @validator('exclude_review_fields', pre=True)
    def fix_exclude_review_fields(cls, value):
        if value is None:
            return set()

        elif isinstance(value, str):
            return [item.strip() for item in value.split(',')]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.ItemReview.__fields__):
                raise errors.ItemReviewExcludeAllFields(
                    excluded_columns=list(unique_values)
                )
            return list(unique_values)

        return value
