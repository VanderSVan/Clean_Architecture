from decimal import Decimal
from typing import Annotated

from pydantic import Field, field_validator

from .base import DTO


class ItemCreateSchema(DTO):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(max_digits=12, decimal_places=2)] = Field(None)
    description: Annotated[str, Field(min_length=1, max_length=1000)] = Field(None)
    category_id: int = Annotated[int, Field(ge=1)]
    type_id: int = Annotated[int, Field(ge=1)]


class ItemGetSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    title: Annotated[str, Field(min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(max_digits=12, decimal_places=2, ge=0)] | None
    description: Annotated[str, Field(min_length=1, max_length=1000)] | None
    category_id: Annotated[int, Field(ge=1)]
    type_id: Annotated[int, Field(ge=1)]
    avg_rating: Annotated[float, Field(ge=1, le=10)] | None

    @field_validator('avg_rating', mode='after')
    def round_avg_rating(cls, value):
        if value:
            return round(value, 2)


class ItemWithHelpedStatusGetSchema(ItemGetSchema):
    is_helped: bool


class ItemWithHelpedStatusSymptomsGetSchema(ItemGetSchema):
    is_helped: bool
    overlapping_symptom_ids: list[int]


class ItemWithHelpedStatusDiagnosisGetSchema(ItemGetSchema):
    is_helped: bool
    diagnosis_id: Annotated[int, Field(ge=1)]


class ItemUpdateSchema(DTO):
    id: Annotated[int, Field(ge=1)]
    title: Annotated[str, Field(min_length=1, max_length=255)] = Field(None)
    price: Annotated[Decimal, Field(max_digits=12, decimal_places=2)] = Field(None)
    description: Annotated[str, Field(min_length=1, max_length=1000)] = Field(None)
    category_id: Annotated[int, Field(ge=1)] = Field(None)
    type_id: Annotated[int, Field(ge=1)] = Field(None)


class ItemDeleteSchema(DTO):
    id: Annotated[int, Field(ge=1)]
