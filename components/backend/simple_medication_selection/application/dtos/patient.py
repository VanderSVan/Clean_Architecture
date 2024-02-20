from enum import Enum
from typing import Annotated

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
    nickname: Annotated[str, Field(..., min_length=1, max_length=255)]
    gender: Annotated[GenderEnum, Field(...)]
    age: Annotated[int, Field(..., ge=10, le=120)]
    skin_type: Annotated[SkinTypeEnum, Field(...)]
    about: Annotated[str, Field(None, min_length=1, max_length=3000)]
    phone: Annotated[
        str, Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')
    ]
    profile_photo_path: Annotated[str, Field(None)]


class PatientGetSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    nickname: Annotated[str, Field(..., min_length=1, max_length=255)]
    gender: Annotated[GenderEnum, Field(...)]
    age: Annotated[int, Field(..., ge=10, le=120)]
    skin_type: Annotated[SkinTypeEnum, Field(...)]
    about: Annotated[str, Field(None, min_length=1, max_length=3000)]
    phone: Annotated[
        str, Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')
    ]
    profile_photo_path: Annotated[str, Field(None)]


class PatientUpdateSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
    nickname: Annotated[str, Field(None, min_length=1, max_length=255)]
    gender: Annotated[GenderEnum, Field(None)]
    age: Annotated[int, Field(None, ge=10, le=120)]
    skin_type: Annotated[SkinTypeEnum, Field(None)]
    about: Annotated[str, Field(None, min_length=1, max_length=3000)]
    phone: Annotated[
        str, Field(None, min_length=9, max_length=15, pattern=r'^([\d]+)$')
    ]
    profile_photo_path: Annotated[str, Field(None)]


class PatientDeleteSchema(DTO):
    id: Annotated[int, Field(..., ge=1)]
