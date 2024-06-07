from pydantic import Field

from med_sharing_system.application import dtos


class ItemReviewOutput(dtos.ItemReview):
    id: int | None = Field(ge=1)
    item_id: int | None = Field(ge=1)
    is_helped: bool | None
    item_rating: float | None = Field(ge=1, le=10, multiple_of=0.5)
    item_count: int | None = Field(ge=1)
    usage_period: int | None = Field(ge=1)
