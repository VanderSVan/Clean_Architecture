from itertools import cycle

from sqlalchemy import insert, select, func, update, Select

from simple_medication_selection.adapters.database import tables
from simple_medication_selection.application import entities

PATIENTS_DATA = [
    {'nickname': 'Иван Иванов', 'gender': 'мужской', 'age': 35, 'skin_type': 'нормальная',
     'about': 'Об Иване Иванове', 'phone': '1234567890'},
    {'nickname': 'Мария Петрова', 'gender': 'женский', 'age': 28, 'skin_type': 'жирная',
     'about': 'О Марии Петровой', 'phone': '0987654321'},
    {'nickname': 'Алексей Сидоров', 'gender': 'мужской', 'age': 42, 'skin_type': 'сухая',
     'about': 'О Алексее Сидорове', 'phone': '5556667777'},
]

DIAGNOSES_DATA = [
    {'name': 'Акне'},
    {'name': 'Экзема'},
    {'name': 'Псориаз'}
]

SYMPTOMS_DATA = [
    {'name': 'Покраснение'},
    {'name': 'Зуд'},
    {'name': 'Сухость'},
    {'name': 'Отек'},
]

CATEGORIES_DATA = [
    {'name': 'Уход за кожей'},
    {'name': 'Уход за волосами'},
    {'name': 'Пищевые добавки'}
]

TYPES_DATA = [
    {'name': 'Крем'},
    {'name': 'Шампунь'},
    {'name': 'Витамин'}
]

ITEMS_DATA = [
    {'title': 'Увлажняющий крем', 'price': 25.99, 'description': 'Увлажняет кожу'},
    {'title': 'Шампунь от перхоти', 'price': 12.50, 'description': 'Удаляет перхоть'},
    {'title': 'Сыворотка с витамином C', 'price': 19.99, 'description': 'Осветляет кожу'},
    {'title': 'Крем против старения', 'price': 30.00, 'description': 'Уменьшает морщины'},
    {'title': 'Дополнение для роста волос', 'price': 29.99,
     'description': 'Способствует росту волос'},
    {'title': 'Ночной крем', 'price': 28.50, 'description': 'Восстанавливает кожу ночью'},
]

REVIEWS_DATA = [
    {'is_helped': True, 'item_rating': 4.5, 'item_count': 10, 'usage_period': 2592000},
    {'is_helped': False, 'item_rating': 3.0, 'item_count': 8, 'usage_period': 5184000},
    {'is_helped': True, 'item_rating': 5.0, 'item_count': 12, 'usage_period': 7776000},
    {'is_helped': True, 'item_rating': 4.0, 'item_count': 6, 'usage_period': 3456000},
    {'is_helped': False, 'item_rating': 2.5, 'item_count': 4, 'usage_period': 1728000},
]

MEDICAL_BOOKS_DATA = [
    {
        'title_history': 'Моя борьба с акне',
        'history': 'Мои трудности и победы над акне',
    },
    {
        'title_history': 'Преодоление экземы',
        'history': 'Как я преодолел экзему',
    },
    {
        'title_history': 'Жизнь с псориазом',
        'history': 'Как справляться с псориазом на ежедневной основе',
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
        {'med_book_id': medical_book_review, 'item_review_id': review_id}
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
    for symptom_count, med_book_id in enumerate(medical_book_ids, start=1):
        symptoms_to_add = symptom_ids[:symptom_count]
        updated_medical_book_symptoms_data.extend(
            [
                {'med_book_id': med_book_id, 'symptom_id': symptom_id}
                for symptom_id in symptoms_to_add
            ]
        )
    medical_book_symptoms_insert = (
        insert(tables.medical_books_symptoms)
        .values(updated_medical_book_symptoms_data)
    )
    session.execute(medical_book_symptoms_insert)


if __name__ == '__main__':
    print("test_data.py script started")
    import logging
    from sqlalchemy import create_engine
    from simple_medication_selection.adapters import database
    from simple_medication_selection.adapters.database import TransactionContext

    logger = logging.getLogger('sqlalchemy')

    engine = create_engine(database.Settings().DATABASE_URL)
    transaction_context = TransactionContext(bind=engine, expire_on_commit=False)

    with transaction_context.current_session as session:
        query: Select = select(tables.medical_books.c.id).limit(1)
        medical_book_exists = bool(session.execute(query).scalars().all())

        if not medical_book_exists:
            logger.info('Inserting test data...')
            patient_ids: list[int] = insert_patients(session)
            diagnosis_ids: list[int] = insert_diagnoses(session)
            symptom_ids: list[int] = insert_symptoms(session)
            category_ids: list[int] = insert_categories(session)
            type_ids: list[int] = insert_types(session)
            item_ids: list[int] = insert_items(type_ids, category_ids, session)
            review_ids: list[int] = insert_reviews(item_ids, session)
            med_book_ids: list[int] = insert_medical_books(patient_ids,
                                                           diagnosis_ids,
                                                           session)
            insert_avg_rating(session)
            insert_medical_book_reviews(med_book_ids, review_ids, session)
            insert_medical_book_symptoms(med_book_ids, symptom_ids, session)
            session.commit()
            logger.info('Test data inserted.')

    print("test_data.py script finished")
