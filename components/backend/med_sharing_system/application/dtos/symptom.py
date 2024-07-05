from med_sharing_system.application.dtos.base import DTO

from pydantic import Field, validator


class Symptom(DTO):
    id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=255, example="Повышенная температура")

    @validator('id', pre=True)
    def convert_id_to_int(cls, value):
        if not isinstance(value, int):
            try:
                return int(value)
            except ValueError:
                raise ValueError('`symptom_id` must be an integer')

        return value

    class Config:
        orm_mode = True


class NewSymptomInfo(DTO):
    name: str = Field(min_length=1, max_length=255, example="Повышенное давление")
