from decimal import Decimal

from pydantic import Field, validator

from .base import DTO
from .item_review import ItemReview


class TreatmentItem(DTO):
    id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2, ge=0)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int = Field(ge=1)
    type_id: int = Field(ge=1)
    avg_rating: float | None = Field(ge=1, le=10)

    @validator('avg_rating', pre=True)
    def round_avg_rating(cls, value):
        if value:
            return round(value, 2)

    def __hash__(self):
        return hash((self.id, self.title, self.price))

    def __eq__(self, other):
        if not isinstance(other, TreatmentItem):
            return False
        return (self.id == other.id and
                self.title == other.title and
                self.price == other.price)

    def dict(self, decode: bool = False, *args, **kwargs):
        data = super().dict(*args, **kwargs)

        if isinstance(data['price'], Decimal) and decode:
            data['price'] = float(self.price)

        return data

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ItemWithReviews(TreatmentItem):
    reviews: list[ItemReview]


class NewItemInfo(DTO):
    title: str = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int = Field(ge=1)
    type_id: int = Field(ge=1)


class UpdatedItemInfo(DTO):
    id: int | None = Field(ge=1)
    title: str | None = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int | None = Field(ge=1)
    type_id: int | None = Field(ge=1)
