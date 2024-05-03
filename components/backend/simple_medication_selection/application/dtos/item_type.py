from .base import DTO

from pydantic import Field


class ItemType(DTO):
    id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=100)

    class Config:
        orm_mode = True


class NewItemTypeInfo(DTO):
    name: str = Field(min_length=1, max_length=100)
