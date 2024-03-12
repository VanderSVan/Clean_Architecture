from itertools import cycle

from sqlalchemy import insert, select, func, update

from simple_medication_selection.adapters.database import tables
from simple_medication_selection.application import entities

PATIENTS_DATA = [
    {'nickname': 'Пациент 1', 'gender': 'male', 'age': 20, 'skin_type': 'нормальная',
     'about': 'О себе 1', 'phone': '1111111111'},
    {'nickname': 'Пациент 2', 'gender': 'female', 'age': 21, 'skin_type': 'жирная',
     'about': 'О себе 2', 'phone': '2222222222'},
    {'nickname': 'Пациент 3', 'gender': 'male', 'age': 22, 'skin_type': 'сухая',
     'about': 'О себе 3', 'phone': '3333333333'},
]

DIAGNOSES_DATA = [
    {'name': 'Диагноз 1'},
    {'name': 'Диагноз 2'},
    {'name': 'Диагноз 3'}
]

SYMPTOMS_DATA = [
    {'name': 'Температура'},
    {'name': 'Давление'},
    {'name': 'Покраснение лица'},
    {'name': 'Симптом 4'},
]

CATEGORIES_DATA = [
    {'name': 'Категория 1'},
    {'name': 'Категория 2'},
    {'name': 'Категория 3'}
]

TYPES_DATA = [
    {'name': 'Тип 1'},
    {'name': 'Тип 2'},
    {'name': 'Тип 3'}
]

ITEMS_DATA = [
    {'title': 'Продукт 1', 'price': 1000.5, 'description': 'Описание 1'},
    {'title': 'Процедура 1', 'price': 3000.55, 'description': 'Описание 2'},
    {'title': 'Продукт 3', 'price': 5000.0, 'description': 'Описание 3'},
    {'title': 'Процедура 2', 'price': 2000.0, 'description': None},
    {'title': 'Продукт 5', 'price': None, 'description': 'Описание 5'},
    {'title': 'Продукт 6', 'price': None, 'description': None},
]

REVIEWS_DATA = [
    {'is_helped': True, 'item_rating': 9.5, 'item_count': 5, 'usage_period': 7776000},
    {'is_helped': False, 'item_rating': 2.0, 'item_count': 3, 'usage_period': 5184000},
    {'is_helped': True, 'item_rating': 8.0, 'item_count': 4, 'usage_period': 2592000},
    {'is_helped': True, 'item_rating': 7.5, 'item_count': 2, 'usage_period': 2592000},
    {'is_helped': False, 'item_rating': 3.5, 'item_count': 1, 'usage_period': 5184000},
    {'is_helped': True, 'item_rating': 6.0, 'item_count': 3, 'usage_period': 2592000},
    {'is_helped': True, 'item_rating': 8.0, 'item_count': 4, 'usage_period': 2592000},
    {'is_helped': True, 'item_rating': 9.0, 'item_count': 5, 'usage_period': 7776000},
]

MEDICAL_BOOKS_DATA = [
    {
        'title_history': 'Как я поборола Розацеа.',
        'history': 'Уот так уот',
    },
    {
        'title_history': 'Как я убрала покраснения.',
        'history': 'Так и так',
    },
    {
        'title_history': 'История моей болезни 3',
        'history': 'Анамнез болезни 3',
    },
    {
        'title_history': 'История моей болезни 4',
        'history': 'Анамнез болезни 4',
    },
]


def insert_patients(session) -> list[int]:
    """Вставляет данные в таблицу `patients`."""
    patients_insert = (
        insert(tables.patients)
        .values(PATIENTS_DATA)
        .returning(tables.patients.c.id)
    )
    return session.execute(patients_insert).scalars().all()


def insert_diagnoses(session) -> list[int]:
    """Вставляет данные в таблицу `diagnoses`."""
    diagnoses_insert = (
        insert(tables.diagnoses)
        .values(DIAGNOSES_DATA)
        .returning(tables.diagnoses.c.id)
    )
    return session.execute(diagnoses_insert).scalars().all()


def insert_symptoms(session) -> list[int]:
    """Вставляет данные в таблицу `symptoms`."""
    symptoms_insert = (
        insert(tables.symptoms)
        .values(SYMPTOMS_DATA)
        .returning(tables.symptoms.c.id)
    )
    return session.execute(symptoms_insert).scalars().all()


def insert_categories(session) -> list[int]:
    """Вставляет данные в таблицу `item_categories`."""
    categories_insert = (
        insert(tables.item_categories)
        .values(CATEGORIES_DATA)
        .returning(tables.item_categories.c.id)
    )
    return session.execute(categories_insert).scalars().all()


def insert_types(session) -> list[int]:
    """Вставляет данные в таблицу `item_types`."""
    types_insert = (
        insert(tables.item_types)
        .values(TYPES_DATA)
        .returning(tables.item_types.c.id)
    )
    return session.execute(types_insert).scalars().all()


def insert_items(type_ids: list[int], category_ids: list[int], session) -> list[int]:
    """Вставляет данные в таблицу `items`."""
    updated_items_data: list[dict] = [
        {**item, 'type_id': type_id, 'category_id': category_id}
        for item, type_id, category_id
        in zip(ITEMS_DATA, cycle(type_ids), cycle(category_ids))
    ]
    items_insert = (
        insert(tables.treatment_items)
        .values(updated_items_data)
        .returning(tables.treatment_items.c.id)
    )
    return session.execute(items_insert).scalars().all()


def insert_reviews(item_ids: list[int], session) -> list[int]:
    """Вставляет данные в таблицу `item_reviews`."""
    updated_reviews_data: list[dict] = [
        {**review, 'item_id': item_id}
        for review, item_id in zip(REVIEWS_DATA, cycle(item_ids[:5]))
    ]
    reviews_insert = (
        insert(tables.item_reviews)
        .values(updated_reviews_data)
        .returning(tables.item_reviews.c.id)
    )
    return session.execute(reviews_insert).scalars().all()


def insert_avg_rating(session):
    """
    Вычисляет средний рейтинг для `entities.TreatmentItem` и
    вставляет полученный результат в бд.
    """
    avg_rating_subquery = (
        select(
            func.avg(entities.ItemReview.item_rating).label('avg_rating'),
            entities.ItemReview.item_id.label('item_id')
        )
        .group_by(entities.ItemReview.item_id)
        .subquery()
    )

    update_query = (
        update(entities.TreatmentItem)
        .where(entities.TreatmentItem.id == avg_rating_subquery.c.item_id)
        .values(avg_rating=avg_rating_subquery.c.avg_rating)
    )

    session.execute(update_query)


def insert_medical_books(patient_ids: list[int],
                         diagnosis_ids: list[int],
                         session
                         ) -> list[int]:
    """Вставляет данные в таблицу `medical_books`."""
    updated_medical_books_data: list[dict] = [
        {**medical_book, 'patient_id': patient_id, 'diagnosis_id': diagnosis_id}
        for medical_book, patient_id, diagnosis_id
        in zip(MEDICAL_BOOKS_DATA, cycle(patient_ids), cycle(diagnosis_ids))
    ]
    medical_books_insert = (
        insert(tables.medical_books)
        .values(updated_medical_books_data)
        .returning(tables.medical_books.c.id)
    )
    return session.execute(medical_books_insert).scalars().all()


def insert_medical_book_reviews(medical_book_ids: list[int],
                                review_ids: list[int],
                                session
                                ) -> None:
    """Вставляет данные в таблицу `medical_books_item_reviews`."""
    updated_medical_book_reviews_data: list[dict] = [
        {'medical_book_id': medical_book_review, 'item_review_id': review_id}
        for medical_book_review, review_id
        in zip(cycle(medical_book_ids), review_ids)
    ]
    medical_book_reviews_insert = (
        insert(tables.medical_books_item_reviews)
        .values(updated_medical_book_reviews_data)
    )
    session.execute(medical_book_reviews_insert)


def insert_medical_book_symptoms(medical_book_ids: list[int],
                                 symptom_ids: list[int],
                                 session
                                 ) -> None:
    """Вставляет данные в таблицу `medical_books_symptoms`."""
    updated_medical_book_symptoms_data: list[dict] = []
    for symptom_count, medical_book_id in enumerate(medical_book_ids, start=1):
        symptoms_to_add = symptom_ids[:symptom_count]
        updated_medical_book_symptoms_data.extend(
            [
                {'medical_book_id': medical_book_id, 'symptom_id': symptom_id}
                for symptom_id in symptoms_to_add
            ]
        )
    medical_book_symptoms_insert = (
        insert(tables.medical_books_symptoms)
        .values(updated_medical_book_symptoms_data)
    )
    session.execute(medical_book_symptoms_insert)
