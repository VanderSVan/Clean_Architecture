from typing import Literal

from pydantic import BaseModel as BaseSchema, Field

from med_sharing_system.application import dtos


class FindPatients(BaseSchema):
    gender: dtos.GenderEnum | None
    age_from: int | None = Field(ge=1)
    age_to: int | None = Field(ge=1)
    skin_type: dtos.SkinTypeEnum | None
    sort_field: Literal[
                    'id', 'nickname', 'gender', 'age', 'skin_type'
                ] | None = 'nickname'
    sort_direction: Literal['asc', 'desc'] | None = 'desc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)
