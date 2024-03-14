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
    nickname: str = Field(..., min_length=1, max_length=255)
    gender: GenderEnum = Field(...)
    age: int = Field(..., ge=10, le=120)
    skin_type: SkinTypeEnum = Field(...)
    about: str = Field(None, min_length=1, max_length=3000)
    phone: str = Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')


class PatientGetSchema(DTO):
    id: int = Field(..., ge=1)
    nickname: str = Field(..., min_length=1, max_length=255)
    gender: GenderEnum = Field(...)
    age: int = Field(..., ge=10, le=120)
    skin_type: SkinTypeEnum = Field(...)
    about: str = Field(None, min_length=1, max_length=3000)
    phone: str = Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')


class PatientUpdateSchema(DTO):
    id: int = Field(..., ge=1)
    nickname: str = Field(None, min_length=1, max_length=255)
    gender: GenderEnum = Field(None)
    age: int = Field(..., ge=10, le=120)
    skin_type: SkinTypeEnum = Field(None)
    about: str = Field(None, min_length=1, max_length=3000)
    phone: str = Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')
