from typing import Annotated

from pydantic import Field

from simple_medication_selection.application.dtos.base import DTO
from simple_medication_selection.application import entities


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


class ItemReviewDeleteSchema(DTO):
    id: Annotated[int, Field(ge=1)]


if __name__ == '__main__':
    review = entities.ItemReview(
        id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
        usage_period=2592000
    )
    dto = ItemReviewUpdateSchema(
        id=1,
        item_id=10001
    )
    dto.populate_obj(review)
    print(review)
