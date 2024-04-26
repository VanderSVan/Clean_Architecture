from enum import Enum

from pydantic import Field

from .base import DTO


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class SkinTypeEnum(str, Enum):
    DRY = 'сухая'
    OILY = 'жирная'
    NORMAL = 'нормальная'
    COMBINATION = 'комбинированная'


class PatientCreateSchema(DTO):
    nickname: str = Field(min_length=1, max_length=255)
    gender: GenderEnum
    age: int = Field(ge=10, le=120)
    skin_type: SkinTypeEnum
    about: str | None = Field(min_length=1, max_length=3000)
    phone: str | None = Field(min_length=9, max_length=15, pattern=r'^([\d]+)$')


class Patient(DTO):
    id: int = Field(ge=1)
    nickname: str = Field(min_length=1, max_length=255)
    gender: GenderEnum
    age: int = Field(ge=10, le=120)
    skin_type: SkinTypeEnum
    about: str | None = Field(min_length=1, max_length=3000)
    phone: str | None = Field(min_length=9, max_length=15, pattern=r'^([\d]+)$')


class PatientUpdateSchema(DTO):
    id: int = Field(ge=1)
    nickname: str | None = Field(min_length=1, max_length=255)
    gender: GenderEnum | None
    age: int | None = Field(ge=10, le=120)
    skin_type: SkinTypeEnum | None
    about: str | None = Field(min_length=1, max_length=3000)
    phone: str | None = Field(min_length=9, max_length=15, pattern=r'^([\d]+)$')
