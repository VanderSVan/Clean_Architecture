from typing import Literal

from pydantic import BaseModel as BaseSchema, Field


class FindDiagnoses(BaseSchema):
    keywords: str | None = Field(max_length=255)
    sort_field: Literal['id', 'name'] = 'name'
    sort_direction: Literal['asc', 'desc'] = 'asc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)
