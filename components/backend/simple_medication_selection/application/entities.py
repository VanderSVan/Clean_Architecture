# Domain слой
import inspect
from dataclasses import dataclass, field, is_dataclass
from typing import Iterable, Literal, Union, TypeAlias
from decimal import Decimal


@dataclass(kw_only=True)
class User:
    id: int
    role: str


@dataclass(kw_only=True)
class AuthorizedUser(User):
    email: str
    password: str
    full_name: str | None
    nickname: str


@dataclass(kw_only=True)
class Patient(AuthorizedUser):
    gender: str
    age: int
    skin_type: str
    about: str | None
    phone: int | None
    profile_photo_path: str | None


@dataclass(kw_only=True)
class Symptom:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class Diagnosis:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class PatientMedicalHistory:
    """
    История пациента с указанием симптомов и диагноза.
    """
    id: int
    title: str
    history: str | None
    patient: Patient
    diagnosis: Diagnosis
    symptoms: list[Symptom] = field(default_factory=list)

    def add_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.append(symptom) if symptom not in self.symptoms else None

    def remove_symptoms(self, symptoms: Iterable[Symptom]) -> None:
        for symptom in symptoms:
            self.symptoms.remove(symptom) if symptom in self.symptoms else None


@dataclass(kw_only=True)
class ItemCategory:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class ItemType:
    id: int | None = None
    name: str


@dataclass(kw_only=True)
class TreatmentItem:
    """
    Данные о продукте или процедуре, которые использовалась во время лечения.
    """
    code: str | None = None
    title: str
    price: Decimal | None = None
    description: str | None = None
    category_id: int
    type_id: int

    def __post_init__(self):
        self.code = self.generate_code(self.category_id, self.type_id, self.title) if not self.code else self.code

    @classmethod
    def generate_code(cls, category_id: int, type_id: int, title: str) -> str:
        return f"{title}-{category_id}-{type_id}"


@dataclass(kw_only=True)
class TreatmentItemFeedback:
    """
    Отзыв о продукте или процедуре.
    """
    id: int
    item: TreatmentItem  # продукт или процедура
    is_helped: bool  # помог / не помог
    item_rating: int  # 1 - 10
    item_count: int  # какое количество процедур или продуктов потребовалось
    usage_period: int | None  # период использования в секундах


@dataclass(kw_only=True)
class CompletedTreatmentProtocol:
    """
    Полный протокол лечения пациента.
    """
    id: int
    patient_medical_history: PatientMedicalHistory
    item_feedbacks: list[TreatmentItemFeedback]
    is_treatment_help: bool

    @property
    def treatment_cost(self) -> float:
        return sum(feedback.item.price * feedback.item_count for feedback in self.item_feedbacks)

    def sort_items_by_rating(self, order: Literal['asc', 'desc'] = 'desc') -> None:
        reverse = True if order == 'desc' else False
        self.item_feedbacks.sort(key=lambda item_feedback: item_feedback.item_rating, reverse=reverse)


# Хранит все сущности в текущем модуле, формируя кортеж
_ENTITIES: tuple = tuple(
    [
        class_obj
        for _, class_obj in inspect.getmembers(inspect.getmodule(inspect.currentframe()))
        if is_dataclass(class_obj)
    ]
)

# Создает объединение типов
Entity: TypeAlias = Union[_ENTITIES]
