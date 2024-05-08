from pydantic import Field

from simple_medication_selection.application.dtos.base import DTO


class ItemReview(DTO):
    id: int | None = Field(ge=1)
    item_id: int | None = Field(ge=1)
    is_helped: bool | None
    item_rating: float | None = Field(ge=1, le=10, multiple_of=0.5)
    item_count: int | None = Field(ge=1)
    usage_period: int | None = Field(ge=1)

    class Config:
        orm_mode = True


class NewItemReviewInfo(DTO):
    item_id: int = Field(ge=1)
    is_helped: bool
    item_rating: float = Field(ge=1, le=10, multiple_of=0.5)
    item_count: int = Field(ge=1)
    usage_period: int | None = Field(ge=1)


class UpdatedItemReviewInfo(DTO):
    id: int = Field(ge=1)
    item_id: int | None = Field(ge=1)
    is_helped: bool | None
    item_rating: float | None = Field(ge=1, le=10, multiple_of=0.5)
    item_count: int | None = Field(ge=1)
    usage_period: int | None = Field(ge=1)
