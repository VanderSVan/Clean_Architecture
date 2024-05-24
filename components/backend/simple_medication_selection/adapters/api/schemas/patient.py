from pydantic import BaseModel as BaseSchema, Field

from simple_medication_selection.application import dtos


class InputUpdatedPatientInfo(BaseSchema):
    nickname: str | None = Field(min_length=1, max_length=255)
    gender: dtos.GenderEnum | None
    age: int | None = Field(ge=10, le=120)
    skin_type: dtos.SkinTypeEnum | None
    about: str | None = Field(min_length=1, max_length=3000)
    phone: str | None = Field(min_length=9, max_length=15, pattern=r'^([\d]+)$')
