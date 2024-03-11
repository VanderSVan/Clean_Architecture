from itertools import cycle

import pytest

from sqlalchemy import insert, select, func, update

from simple_medication_selection.adapters.database import (
    tables,
    repositories
)
from simple_medication_selection.application import entities, dtos

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------

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
    {'name': 'Симптом 1'},
    {'name': 'Симптом 2'},
    {'name': 'Симптом 3'},
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
        'title_history': 'Как убрала покраснения.',
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


@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    patient_ids: list[int] = insert_patients(session)
    diagnosis_ids: list[int] = insert_diagnoses(session)
    symptom_ids: list[int] = insert_symptoms(session)
    category_ids: list[int] = insert_categories(session)
    type_ids: list[int] = insert_types(session)
    item_ids: list[int] = insert_items(type_ids, category_ids, session)
    review_ids: list[int] = insert_reviews(item_ids, session)
    med_book_ids: list[int] = insert_medical_books(patient_ids, diagnosis_ids, session)
    insert_avg_rating(session)
    insert_medical_book_reviews(med_book_ids, review_ids, session)
    insert_medical_book_symptoms(med_book_ids, symptom_ids, session)
    return {
        'patient_ids': patient_ids,
        'diagnosis_ids': diagnosis_ids,
        'symptom_ids': symptom_ids,
        'category_ids': category_ids,
        'type_ids': type_ids,
        'item_ids': item_ids,
        'review_ids': review_ids,
        'med_book_ids': med_book_ids
    }


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.TreatmentItemsRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        item = session.query(entities.TreatmentItem).first()

        # Call
        result = repo.fetch_by_id(item.id)

        # Assert
        assert isinstance(result, entities.TreatmentItem)

    def test__not_found(self, repo, session):
        # Call
        result = repo.fetch_by_id(100)

        # Assert
        assert result is None


class TestFetchAll:
    def test__fetch_all(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field='avg_rating',
                                order_direction='desc',
                                limit=None,
                                offset=None)
        # Assert
        assert len(result) == len(ITEMS_DATA)
        for item in result:
            assert isinstance(item, dtos.ItemGetSchema)

    def test__null_last(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field='avg_rating',
                                order_direction='desc',
                                limit=None,
                                offset=None)

        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field=order_field,
                                order_direction=order_direction,
                                limit=None,
                                offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field=order_field,
                                order_direction=order_direction,
                                limit=None,
                                offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_all(order_field='avg_rating',
                                order_direction='desc',
                                limit=limit,
                                offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_all(order_field='avg_rating',
                                order_direction='desc',
                                limit=None,
                                offset=offset)

        # Assert
        assert len(result) == len(ITEMS_DATA) - offset


class TestFetchAllWithReviews:
    def test__fetch_all_with_reviews(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all_with_reviews(order_field='avg_rating',
                                             order_direction='desc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert len(result) == len(ITEMS_DATA)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)

    def test__null_last(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all_with_reviews(order_field='avg_rating',
                                             order_direction='desc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_all_with_reviews(order_field=order_field,
                                             order_direction=order_direction,
                                             limit=None,
                                             offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_all_with_reviews(order_field=order_field,
                                             order_direction=order_direction,
                                             limit=None,
                                             offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_all_with_reviews(order_field='avg_rating',
                                             order_direction='desc',
                                             limit=limit,
                                             offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_all_with_reviews(order_field='avg_rating',
                                             order_direction='desc',
                                             limit=None,
                                             offset=offset)

        # Assert
        assert len(result) == len(ITEMS_DATA) - offset


class TestFetchByKeywords:
    @pytest.mark.parametrize('keywords, output_item_count', [
        ('продукт', len(ITEMS_DATA) - 2),
        ('процедура', len(ITEMS_DATA) - 4),
        ('про', len(ITEMS_DATA)),
        ('описание', len(ITEMS_DATA) - 2),
        ('продукты', 0),
        ('', len(ITEMS_DATA))
    ])
    def test__fetch_by_keywords(self, keywords, output_item_count, repo, session,
                                fill_db):
        # Call
        result = repo.fetch_by_keywords(keywords=keywords,
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert isinstance(result, list)
        assert len(result) == output_item_count
        for item in result:
            assert isinstance(item, dtos.ItemGetSchema)

    def test__null_last(self, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords(keywords='',
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords(keywords='',
                                        order_field=order_field,
                                        order_direction=order_direction,
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords(keywords='',
                                        order_field=order_field,
                                        order_direction=order_direction,
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_keywords(keywords='',
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=limit,
                                        offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_by_keywords(keywords='',
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=offset)

        # Assert
        assert len(result) == len(ITEMS_DATA) - offset


class TestFetchByKeywordsWithReviews:
    @pytest.mark.parametrize('keywords, output_item_count', [
        ('продукт', len(ITEMS_DATA) - 2),
        ('процедура', len(ITEMS_DATA) - 4),
        ('про', len(ITEMS_DATA)),
        ('описание', len(ITEMS_DATA) - 2),
        ('продукты', 0),
        ('', len(ITEMS_DATA))
    ])
    def test__fetch_by_keywords(self, keywords, output_item_count, repo, session,
                                fill_db):
        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords=keywords,
                                                     order_field='avg_rating',
                                                     order_direction='desc',
                                                     limit=None,
                                                     offset=None)

        # Assert
        assert len(result) == output_item_count
        for item in result:
            assert isinstance(item, entities.TreatmentItem)

    def test__null_last(self, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords='',
                                                     order_field='avg_rating',
                                                     order_direction='desc',
                                                     limit=None,
                                                     offset=None)

        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords='',
                                                     order_field=order_field,
                                                     order_direction=order_direction,
                                                     limit=None,
                                                     offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords='',
                                                     order_field=order_field,
                                                     order_direction=order_direction,
                                                     limit=None,
                                                     offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords='',
                                                     order_field='avg_rating',
                                                     order_direction='desc',
                                                     limit=limit,
                                                     offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_by_keywords_with_reviews(keywords='',
                                                     order_field='avg_rating',
                                                     order_direction='desc',
                                                     limit=None,
                                                     offset=offset)

        # Assert
        assert len(result) == len(ITEMS_DATA) - offset


class TestFetchByCategory:
    def test__fetch_by_category(self, repo, session, fill_db):
        # Setup
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )
        item_count_by_category: int = session.execute(
            select(func.count(entities.TreatmentItem.id.distinct()))
            .where(entities.TreatmentItem.category_id == category_id)
        ).scalar()

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert isinstance(result, list)
        assert len(result) == item_count_by_category
        for item in result:
            assert isinstance(item, dtos.ItemGetSchema)
            assert item.category_id == category_id

    def test__null_last(self, repo, session, fill_db):
        # Setup
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field=order_field,
                                        order_direction=order_direction,
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field=order_field,
                                        order_direction=order_direction,
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=limit,
                                        offset=None)
        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        category_id = (
            session.query(entities.ItemCategory).filter_by(name='Категория 3').first().id
        )
        item_count_by_category: int = session.execute(
            select(func.count(entities.TreatmentItem.id.distinct()))
            .where(entities.TreatmentItem.category_id == category_id)
        ).scalar()

        # Call
        result = repo.fetch_by_category(category_id=category_id,
                                        order_field='avg_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=offset)

        # Assert
        assert len(result) == item_count_by_category - offset


class TestFetchByType:
    def test__fetch_by_type(self, repo, session, fill_db):
        # Setup
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id
        item_count_by_type: int = session.execute(
            select(func.count(entities.TreatmentItem.id.distinct()))
            .where(entities.TreatmentItem.type_id == type_id)
        ).scalar()

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field='avg_rating',
                                    order_direction='desc',
                                    limit=None,
                                    offset=None)

        # Assert
        assert isinstance(result, list)
        assert len(result) == item_count_by_type
        for item in result:
            assert isinstance(item, dtos.ItemGetSchema)
            assert item.type_id == type_id

    def test__null_last(self, repo, session, fill_db):
        # Setup
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field='avg_rating',
                                    order_direction='desc',
                                    limit=None,
                                    offset=None)
        # Assert
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field=order_field,
                                    order_direction=order_direction,
                                    limit=None,
                                    offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field=order_field,
                                    order_direction=order_direction,
                                    limit=None,
                                    offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field='avg_rating',
                                    order_direction='desc',
                                    limit=limit,
                                    offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        type_id = session.query(entities.ItemType).filter_by(name='Тип 3').first().id
        item_count_by_type: int = session.execute(
            select(func.count(entities.TreatmentItem.id.distinct()))
            .where(entities.TreatmentItem.type_id == type_id)
        ).scalar()

        # Call
        result = repo.fetch_by_type(type_id=type_id,
                                    order_field='avg_rating',
                                    order_direction='desc',
                                    limit=None,
                                    offset=offset)

        # Assert
        assert len(result) == item_count_by_type - offset


class TestFetchByRating:
    def test__fetch_by_rating(self, repo, session, fill_db):
        # Setup
        min_rating = 2.5
        max_rating = 9.5

        # Call
        result = repo.fetch_by_rating(
            min_rating=min_rating,
            max_rating=max_rating,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=None
        )
        # Assert
        assert isinstance(result, list)
        # Используется `ITEMS_DATA[:5]` т.к. `Продукту 6` не присвоен рейтинг,
        # потому что он не имеет `entities.ItemReview`
        assert len(result) == len(ITEMS_DATA[:5])
        for item in result:
            assert isinstance(item, dtos.ItemGetSchema)
            assert item.avg_rating >= min_rating
            assert item.avg_rating <= max_rating

    def test__null_last(self, repo, session, fill_db):
        # Setup
        min_rating = 1.0
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field='price',
                                      order_direction='desc',
                                      limit=None,
                                      offset=None)
        # Assert
        assert result[0].price is not None
        assert result[-1].price is None

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        min_rating = 2.5
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field=order_field,
                                      order_direction=order_direction,
                                      limit=None,
                                      offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        min_rating = 2.5
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field=order_field,
                                      order_direction=order_direction,
                                      limit=None,
                                      offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_rating(min_rating=1,
                                      max_rating=10,
                                      order_field='avg_rating',
                                      order_direction='desc',
                                      limit=limit,
                                      offset=None)
        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_by_rating(min_rating=1,
                                      max_rating=10,
                                      order_field='avg_rating',
                                      order_direction='desc',
                                      limit=None,
                                      offset=offset)
        # Assert
        # Используется `ITEMS_DATA[:5]` т.к. `Продукту 6` не присвоен рейтинг,
        # потому что он не имеет `entities.ItemReview`
        assert len(result) == len(ITEMS_DATA[:5]) - offset


class TestFetchByHelpedStatus:
    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status(self, helped_status, repo, session, fill_db):
        # Setup
        helped_item_ids: list[int] = (
            session.execute(
                select(entities.TreatmentItem.id)
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == helped_status)
                .distinct(entities.TreatmentItem.id)
            ).scalars().all()
        )

        # Call
        result = repo.fetch_by_helped_status(
            is_helped=helped_status,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=None
        )

        # Assert
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dtos.ItemWithHelpedStatusGetSchema)
            assert item.id in helped_item_ids
            assert item.is_helped == helped_status

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_helped_status(
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Call
        result = repo.fetch_by_helped_status(
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_helped_status(
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=limit,
            offset=None
        )
        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        helped_status = True
        helped_items_count: int = (
            session.execute(
                select(func.count(entities.TreatmentItem.id.distinct()))
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == helped_status)
            ).scalar()
        )

        # Call
        result = repo.fetch_by_helped_status(
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=offset
        )
        # Assert
        assert len(result) == helped_items_count - offset


class TestFetchBySymptomsAndHelpedStatus:
    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_symptoms_and_helped_status(self, helped_status, repo, session,
                                                  fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        helped_item_ids: list[int] = (
            session.execute(
                select(entities.ItemReview.item_id)
                .join(entities.MedicalBook.item_reviews)
                .join(entities.MedicalBook.symptoms)
                .where(
                    entities.ItemReview.is_helped == helped_status,
                    entities.Symptom.id.in_(symptom_ids)
                )
                .distinct(entities.ItemReview.item_id)
            ).scalars().all()
        )

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            is_helped=helped_status,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=None
        )

        # Assert
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dtos.ItemWithHelpedStatusSymptomsGetSchema)
            assert item.id in helped_item_ids
            assert item.is_helped == helped_status
            assert all(
                symptom_id in symptom_ids for symptom_id in item.overlapping_symptom_ids
            )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids=fill_db['symptom_ids'],
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=limit,
            offset=None
        )

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        helped_status = True
        helped_item_count: int = (
            session.execute(
                select(func.count(entities.ItemReview.item_id.distinct()))
                .join(entities.MedicalBook.item_reviews)
                .join(entities.MedicalBook.symptoms)
                .where(
                    entities.ItemReview.is_helped == helped_status,
                    entities.Symptom.id.in_(symptom_ids)
                )
            ).scalar()
        )
        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=offset
        )
        # Assert
        assert len(result) == helped_item_count - offset


class TestFetchByDiagnosisAndHelpedStatus:
    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_diagnosis_and_helped_status(self, helped_status, repo, session,
                                                   fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        helped_item_ids: list[int] = (
            session.execute(
                select(entities.ItemReview.item_id)
                .join(entities.MedicalBook.item_reviews)
                .where(
                    entities.ItemReview.is_helped == helped_status,
                    entities.MedicalBook.diagnosis_id == diagnosis_id
                )
                .distinct(entities.ItemReview.item_id)
            ).scalars().all()
        )

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id=diagnosis_id,
            is_helped=helped_status,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=None
        )

        # Assert
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, dtos.ItemWithHelpedStatusDiagnosisGetSchema)
            assert item.id in helped_item_ids
            assert item.is_helped == helped_status
            assert item.diagnosis_id == diagnosis_id

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'asc'),
        ('title', 'asc'),
        ('price', 'asc'),
        ('category_id', 'asc'),
        ('type_id', 'asc'),
        ('avg_rating', 'asc'),

    ])
    def test__order_is_asc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id=diagnosis_id,
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    @pytest.mark.parametrize('order_field, order_direction', [
        ('id', 'desc'),
        ('title', 'desc'),
        ('price', 'desc'),
        ('category_id', 'desc'),
        ('type_id', 'desc'),
        ('avg_rating', 'desc'),
    ])
    def test__order_is_desc(self, order_field, order_direction, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id=diagnosis_id,
            is_helped=True,
            order_field=order_field,
            order_direction=order_direction,
            limit=None,
            offset=None
        )

        # Assert
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf') if getattr(treatment_item, order_field) is None
                else getattr(treatment_item, order_field)
            ),
            reverse=True if order_direction == 'desc' else False
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=limit,
            offset=None
        )

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        helped_status = True
        helped_item_count: int = (
            session.execute(
                select(func.count(entities.ItemReview.item_id.distinct()))
                .join(entities.MedicalBook.item_reviews)
                .where(
                    entities.ItemReview.is_helped == helped_status,
                    entities.MedicalBook.diagnosis_id == diagnosis_id
                )
            ).scalar()
        )

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            is_helped=True,
            order_field='avg_rating',
            order_direction='desc',
            limit=None,
            offset=offset
        )

        # Assert
        assert len(result) == helped_item_count - offset


class TestAdd:
    def test__add(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.treatment_items.select()).all())
        reviews_to_add: list[entities.ItemReview] = (
            session.query(entities.ItemReview)
            .filter(
                entities.ItemReview.id.in_(
                    [fill_db['review_ids'][0], fill_db['review_ids'][1]]
                )
            )
            .all()
        )

        # Call
        result = repo.add(
            entities.TreatmentItem(
                title='Title 1',
                price=1000.50,
                description='Description 1',
                category_id=fill_db['category_ids'][0],
                type_id=fill_db['type_ids'][0],
                reviews=reviews_to_add
            )
        )
        after_count = len(session.execute(tables.treatment_items.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.TreatmentItem)

    def test__add_with_no_reviews(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.treatment_items.select()).all())

        # Call
        result = repo.add(
            entities.TreatmentItem(
                title='Title 1',
                price=1000.50,
                description='Description 1',
                category_id=fill_db['category_ids'][0],
                type_id=fill_db['type_ids'][0],
            )
        )
        after_count = len(session.execute(tables.treatment_items.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.TreatmentItem)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.treatment_items.select()).all())
        treatment_item: entities.TreatmentItem = session.query(entities.TreatmentItem).first()

        # Call
        result = repo.remove(treatment_item)
        after_count = len(session.execute(tables.treatment_items.select()).all())

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.TreatmentItem)
