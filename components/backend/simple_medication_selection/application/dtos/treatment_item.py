from decimal import Decimal
from typing import Annotated

from pydantic import Field, computed_field

from .base import DTO
from .. import entities


class TreatmentItemCreateSchema(DTO):
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: int = Field(..., ge=1)
    type_id: int = Field(..., ge=1)

    @computed_field
    @property
    def code(self) -> str:
        return entities.TreatmentItem.generate_code(self.category_id, self.type_id, self.title)


class TreatmentItemGetSchema(DTO):
    code: Annotated[str, Field(..., min_length=1, max_length=255)]
    title: Annotated[str, Field(..., min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: Annotated[int, Field(..., ge=1)]
    type_id: Annotated[int, Field(..., ge=1)]


class TreatmentItemUpdateSchema(DTO):
    code: Annotated[str, Field(..., min_length=1, max_length=255)]
    title: Annotated[str, Field(None, min_length=1, max_length=255)]
    price: Annotated[Decimal, Field(None, max_digits=12, decimal_places=2)]
    description: Annotated[str, Field(None, min_length=1, max_length=1000)]
    category_id: Annotated[int, Field(None, ge=1)]
    type_id: Annotated[int, Field(None, ge=1)]


class TreatmentItemDeleteSchema(DTO):
    code: Annotated[str, Field(..., min_length=1, max_length=255)]
