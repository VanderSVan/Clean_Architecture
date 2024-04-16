from typing import Literal

from pydantic import BaseModel as BaseSchema, Field, validator, root_validator


class FindMedicalBooks(BaseSchema):
    patient_id: int | None = Field(ge=1)
    item_ids: list[int] | None = Field(ge=1)
    is_helped: bool | None
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    match_all_symptoms: bool | None = Field(description='Полное совпадение со всеми '
                                                        'симптомами  одновременно')
    sort_field: Literal[
                    'id', 'title_history', 'history', 'patient_id', 'diagnosis_id'] | None
    sort_direction: Literal['asc', 'desc'] | None
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)

    @validator('item_ids', pre=True)
    def fix_item_ids(cls, value):
        if value is not None and not isinstance(value, list):
            return [value]

        if isinstance(value, list):
            return set(value)

        return value

    @validator('symptom_ids', pre=True)
    def fix_symptom_ids(cls, value):
        if value is not None and not isinstance(value, list):
            return [value]

        if isinstance(value, list):
            return set(value)

        return value

    @root_validator
    def fix_match_all_symptoms(cls, values):
        if values['symptom_ids'] is None and values['match_all_symptoms'] is not None:
            values['match_all_symptoms'] = None
            return values

        return values
