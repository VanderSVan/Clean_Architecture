from typing import Literal

from pydantic import BaseModel as BaseSchema, Field, validator, root_validator

from med_sharing_system.application import dtos, errors


class GetTreatmentItem(BaseSchema):
    item_id: int = Field(ge=1)


class GetTreatmentItemWithReviews(GetTreatmentItem):
    reviews_sort_field: (
        Literal['id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period']
        | None
    ) = None
    reviews_sort_direction: Literal['asc', 'desc'] | None = 'asc'
    reviews_limit: int | None = Field(10, ge=1)
    reviews_offset: int | None = Field(0, ge=0)
    exclude_review_fields: list[Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ]] | None = None


class FindTreatmentItems(BaseSchema):
    keywords: str | None = Field(max_length=255)
    is_helped: bool | None
    diagnosis_id: int | None = Field(ge=1)
    symptom_ids: list[int] | None = Field(ge=1)
    match_all_symptoms: bool | None = Field(description='Совпадение со всеми симптомами '
                                                        'одновременно')
    min_rating: float | None = Field(ge=0, le=10)
    max_rating: float | None = Field(ge=1, le=10)
    min_price: float | None = Field(ge=0)
    max_price: float | None = Field(ge=1)
    category_id: int | None = Field(ge=1)
    type_id: int | None = Field(ge=1)
    sort_field: Literal['price', 'avg_rating', 'title'] = 'avg_rating'
    sort_direction: Literal['asc', 'desc'] = 'desc'
    limit: int | None = Field(10, ge=1)
    offset: int | None = Field(0, ge=0)
    exclude_item_fields: list[Literal[
        'title', 'price', 'description', 'category_id', 'type_id', 'avg_rating'
    ]] | None = None

    @validator('symptom_ids', pre=True)
    def fix_symptom_ids(cls, value):
        if value is not None and not isinstance(value, list):
            return list(value)

        if isinstance(value, list):
            return set(value)

        return value

    @root_validator
    def fix_match_all_symptoms(cls, values):
        if (
            values.get('symptom_ids') is None and
            values.get('match_all_symptoms') is not None
        ):
            values['match_all_symptoms'] = None
            return values

        return values

    @validator('exclude_item_fields', pre=True)
    def fix_exclude_item_fields(cls, value):
        if value is None:
            return set()

        elif isinstance(value, str):
            return [item.strip() for item in value.split(',')]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.TreatmentItem.__fields__):
                raise errors.TreatmentItemExcludeAllFields(
                    excluded_columns=list(unique_values)
                )
            return set(value)

        return value


class FindTreatmentItemsWithReviews(FindTreatmentItems):
    reviews_sort_field: (
        Literal['id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period']
        | None
    ) = None
    reviews_sort_direction: Literal['asc', 'desc'] | None = None
    reviews_limit: int | None = Field(10, ge=1)
    reviews_offset: int | None = Field(0, ge=0)
    exclude_review_fields: list[Literal[
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period'
    ]] | None = None

    @validator('exclude_review_fields', pre=True)
    def fix_exclude_review_fields(cls, value):
        if value is None:
            return set()

        elif isinstance(value, str):
            return [item.strip() for item in value.split(',')]

        elif isinstance(value, list):
            unique_values = set(value)
            if len(unique_values) == len(dtos.ItemReview.__fields__):
                raise errors.ItemReviewExcludeAllFields(
                    excluded_columns=list(unique_values)
                )
            return list(unique_values)

        return value
