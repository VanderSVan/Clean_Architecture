from typing import Literal

from pydantic import BaseModel as BaseSchema, Field, validator


class FindMedicalBooks(BaseSchema):
    items: list[int] | None = Field(ge=1)
    is_helped: bool | None
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    match_all_symptoms: bool | None = Field(description='Полное совпадение со всеми '
                                                        'симптомами  одновременно')
    sort_field: Literal['patient_id', 'diagnosis_id', 'title_history'] = 'diagnosis_id'
    sort_direction: Literal['asc', 'desc'] = 'desc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)

    @validator('symptom_ids', pre=True)
    def fix_symptom_ids(cls, value):
        if value is not None and not isinstance(value, list):
            return list(value)

        if isinstance(value, list):
            return set(value)

        return value

    # @validator('match_all_symptoms', pre=True)
    # def fix_match_all_symptoms(cls, value):
    #     if cls.symptom_ids is None and value is not None:
    #         return None
    #
    #     return value


class FindPatientMedicalBooks(FindMedicalBooks):
    patient_id: int = Field(ge=1)

