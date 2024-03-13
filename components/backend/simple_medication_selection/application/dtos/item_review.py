from typing import Annotated

from pydantic import Field

from simple_medication_selection.application.dtos.base import DTO


class ItemReviewCreateSchema(DTO):
    item_id: Annotated[int, Field(ge=1)]
    is_helped: bool
    item_rating: Annotated[float, Field(ge=1, le=10, multiple_of=0.5)]
    item_count: Annotated[int, Field(ge=1)]
    usage_period: Annotated[int, Field(ge=1)] = Field(None)


class ItemReviewGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    item_id: Annotated[int, Field(ge=1)]
    is_helped: bool
    item_rating: Annotated[float, Field(ge=1, le=10, multiple_of=0.5)]
    item_count: Annotated[int, Field(ge=1)]
    usage_period: Annotated[int, Field(ge=1)]


class ItemReviewUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    item_id: Annotated[int, Field(ge=1)] = Field(None)
    is_helped: bool = Field(None)
    item_rating: Annotated[float, Field(ge=1, le=10, multiple_of=0.5)] = Field(None)
    item_count: Annotated[int, Field(ge=1)] = Field(None)
    usage_period: Annotated[int, Field(ge=1)] = Field(None)
