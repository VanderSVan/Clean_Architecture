# Domain слой
import inspect
from dataclasses import dataclass, field, is_dataclass
from statistics import mean
from typing import Iterable, Union, TypeAlias, Literal
from decimal import Decimal


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

    def get_avg_rating(self) -> float | None:
        if self.reviews and not self.avg_rating:
            return mean([review.item_rating for review in self.reviews])

        return self.avg_rating


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

    def add_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.append(symptom) if symptom not in self.symptoms else None

    def remove_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.remove(symptom) if symptom in self.symptoms else None

    def sort_items_by_rating(self, order: Literal['asc', 'desc'] = 'desc') -> None:
        reverse = True if order == 'desc' else False
        self.item_reviews.sort(
            key=lambda item_review: item_review.item_rating, reverse=reverse
        )

    def get_items_by_helped_status(self,
                                   is_helped: bool = True,
                                   *,
                                   order_by_rating: Literal['asc', 'desc'] = 'desc'
                                   ) -> list[TreatmentItem]:
        self.sort_items_by_rating(order_by_rating)
        return [
            item_review.item
            for item_review in self.item_reviews
            if item_review.is_helped == is_helped
        ]


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
