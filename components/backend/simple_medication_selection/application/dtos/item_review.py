from pydantic import Field

from simple_medication_selection.application.dtos.base import DTO


class ItemReviewCreateSchema(DTO):
    item_id: int = Field(..., ge=1)
    is_helped: bool
    item_rating: float = Field(..., ge=1, le=10, multiple_of=0.5)
    item_count: int = Field(..., ge=1)
    usage_period: int = Field(None, ge=1)


class ItemReviewGetSchema(DTO):
    id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)
    is_helped: bool
    item_rating: float = Field(..., ge=1, le=10, multiple_of=0.5)
    item_count: int = Field(..., ge=1)
    usage_period: int | None = Field(None, ge=1)


class ItemReviewUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    item_id: int = Field(None, ge=1)
    is_helped: bool = Field(None)
    item_rating: float = Field(None, ge=1, le=10, multiple_of=0.5)
    item_count: int = Field(None, ge=1)
    usage_period: int = Field(None, ge=1)
