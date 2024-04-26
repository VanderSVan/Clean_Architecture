from pydantic import BaseModel as BaseSchema, Field

from simple_medication_selection.application import dtos


class FindPatients(BaseSchema):
    nickname: str | None = Field(min_length=1, max_length=255)
    gender: dtos.GenderEnum | None
    age_from: int | None = Field(ge=1)
    age_to: int | None = Field(ge=1)
    skin_type: dtos.SkinTypeEnum | None

