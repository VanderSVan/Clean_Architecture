# Domain слой
import inspect
from dataclasses import dataclass, field, is_dataclass, asdict
from decimal import Decimal
from statistics import mean
from typing import Iterable, Union, TypeAlias


@dataclass(kw_only=True)
class Patient:
    id: int | None = None
    nickname: str
    gender: str
    age: int
    skin_type: str
    about: str | None = None
    phone: str | None = None


@dataclass(kw_only=True)
class Symptom:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class Diagnosis:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class ItemCategory:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class ItemType:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class ItemReview:
    """
    Отзыв пациента о продукте или процедуре.
    """
    id: int | None = None
    item_id: int  # продукт или процедура `TreatmentItem`
    is_helped: bool  # помог / не помог
    item_rating: float  # От 1 до 10 с шагом 0.5.
    item_count: int  # какое количество процедур или продуктов потребовалось
    usage_period: int | None = None  # период использования в секундах

    @classmethod
    def get_field_names(cls, exclude_fields: list[str] | None = None) -> list[str]:
        fields: list[str] = cls.__dataclass_fields__.keys()

        if exclude_fields is None:
            return fields

        return [field_name for field_name in fields if field_name not in exclude_fields]


@dataclass(kw_only=True)
class TreatmentItem:
    """
    Данные о продукте или процедуре, которые использовалась во время лечения.
    """
    id: int | None = None
    title: str
    price: Decimal | None = None
    description: str | None = None
    category_id: int
    type_id: int
    reviews: list[ItemReview] = field(default_factory=list)
    avg_rating: float | None = None

    def __hash__(self):
        return hash((self.id, self.title, self.price))

    def __eq__(self, other):
        if not isinstance(other, TreatmentItem):
            return False

        return (self.id == other.id and
                self.title == other.title and
                self.price == other.price)

    @classmethod
    def get_field_names(cls,
                        exclude_fields: list[str] | None = None,
                        exclude_nested_fields: bool = False
                        ) -> list[str]:
        fields: list[str] = cls.__dataclass_fields__.keys()

        if exclude_fields is None:
            return fields

        elif exclude_fields and exclude_nested_fields and 'reviews' not in exclude_fields:
            exclude_fields.append('reviews')

        return [field_name for field_name in fields if field_name not in exclude_fields]

    def get_avg_rating(self) -> float | None:
        if self.reviews and not self.avg_rating:
            return mean([review.item_rating for review in self.reviews])

        return self.avg_rating

    def to_dict(self) -> dict:
        data = asdict(self)

        if data['price'] is not None:
            data['price'] = float(data['price'])

        return data


@dataclass(kw_only=True)
class MedicalBook:
    """
    Медицинская карта пациента.
    """
    id: int | None = None
    title_history: str
    history: str | None = None
    patient_id: int
    diagnosis_id: int
    symptoms: list[Symptom] = field(default_factory=list)
    item_reviews: list[ItemReview] = field(default_factory=list)

    def __hash__(self):
        return hash((self.id, self.patient_id, self.diagnosis_id))

    def __eq__(self, other):
        if not isinstance(other, MedicalBook):
            return False

        return (self.id == other.id and
                self.patient_id == other.patient_id and
                self.diagnosis_id == other.diagnosis_id)

    def add_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.append(symptom) if symptom not in self.symptoms else None

    def remove_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.remove(symptom) if symptom in self.symptoms else None

    def add_item_reviews(self, item_reviews: Iterable[ItemReview]) -> None:
        for item_review in item_reviews:
            (self.item_reviews.append(item_review)
             if item_review not in self.item_reviews else None)

    def remove_item_reviews(self, item_reviews: Iterable[ItemReview]) -> None:
        for item_review in item_reviews:
            (self.item_reviews.remove(item_review)
             if item_review in self.item_reviews else None)


# Хранит все сущности из текущего модуля, формируя кортеж
_ENTITIES = tuple(
    [
        class_obj
        for _, class_obj in inspect.getmembers(inspect.getmodule(inspect.currentframe()))
        if is_dataclass(class_obj)
    ]
)

# Создает объединяющий тип для всех сущностей
Entity: TypeAlias = Union[_ENTITIES]
