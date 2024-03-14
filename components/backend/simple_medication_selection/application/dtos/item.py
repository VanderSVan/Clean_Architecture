from decimal import Decimal

from pydantic import Field, validator

from .base import DTO


class ItemCreateSchema(DTO):
    title: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(None, max_digits=12, decimal_places=2)
    description: str = Field(None, min_length=1, max_length=1000)
    category_id: int = Field(..., ge=1)
    type_id: int = Field(..., ge=1)


class ItemGetSchema(DTO):
    id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(None, max_digits=12, decimal_places=2, ge=0)
    description: str = Field(None, min_length=1, max_length=1000)
    category_id: int = Field(..., ge=1)
    type_id: int = Field(..., ge=1)
    avg_rating: float = Field(None, ge=1, le=10)

    @validator('avg_rating', pre=True)
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
    diagnosis_id: int = Field(..., ge=1)


class ItemUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    title: str = Field(None, min_length=1, max_length=255)
    price: Decimal = Field(None, max_digits=12, decimal_places=2)
    description: str = Field(None, min_length=1, max_length=1000)
    category_id: int = Field(None, ge=1)
    type_id: int = Field(None, ge=1)
