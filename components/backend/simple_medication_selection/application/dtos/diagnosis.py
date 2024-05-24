from pydantic import Field

from .base import DTO


class Diagnosis(DTO):
    id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=100)

    class Config:
        orm_mode = True


class NewDiagnosisInfo(DTO):
    name: str = Field(min_length=1, max_length=100)
