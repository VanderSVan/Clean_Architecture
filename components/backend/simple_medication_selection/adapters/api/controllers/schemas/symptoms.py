from typing import Literal

from pydantic import BaseModel as BaseSchema, Field


class FindSymptoms(BaseSchema):
    keywords: str = Field('', min_length=1, max_length=255)
    sort_field: Literal['id', 'name']
    sort_direction: Literal['asc', 'desc']
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)
