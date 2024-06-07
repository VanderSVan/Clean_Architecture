from typing import Literal

from pydantic import Field, validator, root_validator

from med_sharing_system.application import schemas, dtos, errors
from .symptom import SymptomOutput
from .item_review import ItemReviewOutput


class SearchMedicalBooks(schemas.FindMedicalBooks):
    exclude_med_book_fields: list[Literal[
        'id', 'title_history', 'history', 'patient_id', 'diagnosis_id']] | None

    @validator('exclude_med_book_fields', pre=True)
    def fix_exclude_main_fields(cls, value):
        if value is None:
            return set()

        elif value is not None and not isinstance(value, list):
            return [value]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.MedicalBook.__fields__):
                raise errors.MedicalBookExcludeAllFields(
                    excluded_columns=list(unique_values)
                )
            return set(value)

        return value

    @root_validator
    def fix_sort_field(cls, values):
        if not values.get('exclude_med_book_fields'):
            return values

        elif values['sort_field'] in values['exclude_med_book_fields']:
            raise errors.MedicalBookExcludeSortField(
                excluded_columns=values['exclude_med_book_fields'],
                sort_field=values['sort_field']
            )

        return values


class SearchMedicalBooksWithSymptoms(SearchMedicalBooks):
    exclude_symptom_fields: list[Literal['id', 'name']] | None

    @validator('exclude_symptom_fields', pre=True)
    def fix_exclude_fields_for_symptoms(cls, value):
        if value is None:
            return set()

        elif value is not None and not isinstance(value, list):
            return [value]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.Symptom.__fields__):
                raise errors.SymptomExcludeAllFields(excluded_columns=list(unique_values))
            return set(value)

        return value


class SearchMedicalBooksWithItemReviews(SearchMedicalBooks):
    exclude_item_review_fields: list[Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period']] | None

    @validator('exclude_item_review_fields', pre=True)
    def fix_exclude_fields_for_item_reviews(cls, value):
        if value is None:
            return set()

        elif value is not None and not isinstance(value, list):
            return [value]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.ItemReview.__fields__):
                raise errors.ItemReviewExcludeAllFields(
                    excluded_columns=list(unique_values)
                )
            return set(value)

        return value


class SearchMedicalBooksWithSymptomsAndItemReviews(SearchMedicalBooksWithSymptoms,
                                                   SearchMedicalBooksWithItemReviews):
    pass


class MedicalBookOutput(dtos.MedicalBook):
    id: int | None = Field(ge=1)
    title_history: str | None = Field(min_length=1, max_length=255,
                                      example="Заголовок история болезни")
    history: str | None = Field(min_length=1, max_length=15000, example="История болезни")
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)


class MedicalBookWithSymptomsOutput(MedicalBookOutput):
    symptoms: list[SymptomOutput | None] | None


class MedicalBookWithItemReviewsOutput(MedicalBookOutput):
    item_reviews: list[ItemReviewOutput | None] | None


class MedicalBookWithSymptomsAndItemReviewsOutput(MedicalBookWithSymptomsOutput,
                                                  MedicalBookWithItemReviewsOutput):
    pass


class PutMedicalBookInfo(dtos.DTO):
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    item_review_ids: list[int] | None = Field(ge=1)


class PatchMedicalBookInfo(dtos.DTO):
    title_history: str | None = Field(min_length=1, max_length=255)
    history: str | None = Field(min_length=1, max_length=15000)
    patient_id: int | None = Field(ge=1)
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids_to_add: list[int] | None = Field(ge=1)
    item_review_ids_to_add: list[int] | None = Field(ge=1)
    symptom_ids_to_remove: list[int] | None = Field(ge=1)
    item_review_ids_to_remove: list[int] | None = Field(ge=1)
