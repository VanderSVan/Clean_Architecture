from decimal import Decimal

from pydantic import Field, validator

from .base import DTO
from .item_review import ItemReview


class TreatmentItem(DTO):
    id: int | None = Field(ge=1)
    title: str | None = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2, ge=0)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int | None = Field(ge=1)
    type_id: int | None = Field(ge=1)
    avg_rating: float | None = Field(ge=1, le=10)

    @validator('avg_rating', pre=True)
    def round_avg_rating(cls, value):
        if value:
            return round(value, 2)

    def dict(self, decode: bool = False, *args, **kwargs):
        data = super().dict(*args, **kwargs)

        if isinstance(data.get('price'), Decimal) and decode:
            data['price'] = float(self.price)

        return data

    class Config:
        orm_mode = True
        json_encoders = {Decimal: lambda v: float(v)}


class TreatmentItemWithReviews(TreatmentItem):
    reviews: list[ItemReview]


class NewTreatmentItemInfo(DTO):
    title: str = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int = Field(ge=1)
    type_id: int = Field(ge=1)


class UpdatedTreatmentItemInfo(DTO):
    id: int = Field(ge=1)
    title: str | None = Field(min_length=1, max_length=255)
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    description: str | None = Field(min_length=1, max_length=1000)
    category_id: int | None = Field(ge=1)
    type_id: int | None = Field(ge=1)
