from itertools import cycle
from typing import Sequence
import random
import pytest

from sqlalchemy import insert, and_, desc

from simple_medication_selection.adapters.database import (
    tables,
    repositories
)
from simple_medication_selection.application import entities

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
    {'title': 'Продукт 2', 'price': 3000.55, 'description': 'Описание 2'},
    {'title': 'Продукт 3', 'price': 5000.0, 'description': 'Описание 3'},
    {'title': 'Продукт 4', 'price': 2000.0, 'description': 'Описание 4'},
    {'title': 'Продукт 5', 'price': 4000.0, 'description': 'Описание 5'},
]

REVIEWS_DATA = [
    {'is_helped': True, 'item_rating': 9.5, 'item_count': 5, 'usage_period': 7776000},
    {'is_helped': False, 'item_rating': 2.0, 'item_count': 3, 'usage_period': 5184000},
    {'is_helped': True, 'item_rating': 8.0, 'item_count': 4, 'usage_period': 2592000},
    {'is_helped': True, 'item_rating': 7.5, 'item_count': 2, 'usage_period': 2592000},
    {'is_helped': False, 'item_rating': 3.5, 'item_count': 1, 'usage_period': 5184000},

]

MEDICAL_BOOK_SYMPTOMS_DATA = [
    {'medical_book_id': 1, 'symptom_id': 1},
    {'medical_book_id': 1, 'symptom_id': 2},
    {'medical_book_id': 2, 'symptom_id': 1},
    {'medical_book_id': 2, 'symptom_id': 3},
    {'medical_book_id': 3, 'symptom_id': 2},
    {'medical_book_id': 3, 'symptom_id': 3}
]

MEDICAL_BOOK_ITEM_REVIEWS_DATA = [
    {'medical_book_id': 1, 'item_review_id': 1},
    {'medical_book_id': 1, 'item_review_id': 2},
    {'medical_book_id': 2, 'item_review_id': 1},
    {'medical_book_id': 2, 'item_review_id': 3},
    {'medical_book_id': 3, 'item_review_id': 2},
    {'medical_book_id': 3, 'item_review_id': 3}
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
    {
        'title_history': 'История моей болезни 5',
        'history': 'Анамнез болезни 5',
    }
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
        for review, item_id in zip(REVIEWS_DATA, item_ids)
    ]
    reviews_insert = (
        insert(tables.item_reviews)
        .values(updated_reviews_data)
        .returning(tables.item_reviews.c.id)
    )
    return session.execute(reviews_insert).scalars().all()


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
        in zip(medical_book_ids, cycle(review_ids))
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
    shuffled_symptom_ids = random.sample(symptom_ids, len(symptom_ids))
    updated_medical_book_symptoms_data: list[dict] = []

    for medical_book_id in medical_book_ids:
        symptom_count = random.randint(len(symptom_ids) - 1, len(symptom_ids))
        symptoms_to_add = shuffled_symptom_ids[:symptom_count]
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
    return repositories.MedicalBooksRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchAll:
    def test_fetch_all(self, repo, session):
        # Call
        result = repo.fetch_all(limit=None, offset=None)

        # Assert
        assert len(result) == len(MEDICAL_BOOKS_DATA)
        assert isinstance(result[0], entities.MedicalBook)

    def test__fetch_all__with_limit(self, repo):
        # Call
        result = repo.fetch_all(limit=1, offset=None)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], entities.MedicalBook)

    def test__fetch_all__with_offset(self, repo):
        # Call
        result = repo.fetch_all(limit=None, offset=1)

        # Assert
        assert len(result) == len(MEDICAL_BOOKS_DATA) - 1

    def test__fetch_all__empty_result(self, repo):
        # Call
        result = repo.fetch_all(limit=100, offset=100)

        # Assert
        assert len(result) == 0
        assert result == []


class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id(med_book.id)

        # Assert
        assert result is not None
        assert isinstance(result, entities.MedicalBook)

    def test__fetch_by_id__not_found(self, repo):
        # Call
        result = repo.fetch_by_id(100)

        # Assert
        assert result is None


class TestFetchByPatientId:
    def test__fetch_by_patient_id(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_patient(med_book.patient_id)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)

    def test__fetch_by_patient_id__with_limit(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_patient(med_book.patient_id, limit=1)

        # Assert
        assert len(result) == 1

    def test__fetch_by_patient_id__with_offset(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()
        med_books_by_patient = (
            session.query(entities.MedicalBook).filter_by(patient_id=patient.id).all()
        )

        # Call
        result = (
            repo.fetch_by_patient(med_books_by_patient[0].patient_id, offset=1)
        )

        # Assert
        assert len(result) == len(med_books_by_patient) - 1
        assert med_books_by_patient[1:] == result
        for med_book in result:
            assert med_book.patient_id == patient.id

    def test__fetch_by_patient_id__not_found(self, repo):
        # Call
        result = repo.fetch_by_patient(100)

        # Assert
        assert result == []


class TestFetchBySymptoms:
    def test__fetch_by_symptoms(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:3]

        # Call
        result = repo.fetch_by_symptoms(symptom_ids)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)

    def test__fetch_by_symptoms__with_limit(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:3]

        # Call
        result = repo.fetch_by_symptoms(symptom_ids, limit=1)

        # Assert
        assert len(result) == 1

    def test__fetch_by_symptoms__with_offset(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        med_books_by_symptoms = (
            session.query(entities.MedicalBook)
            .filter(
                entities.MedicalBook.symptoms.any(entities.Symptom.id.in_(symptom_ids))
            )
            .all()
        )

        # Call
        result = repo.fetch_by_symptoms(symptom_ids, offset=1)

        # Assert
        assert len(result) == len(med_books_by_symptoms) - 1
        assert med_books_by_symptoms[1:] == result
        for med_book in result:
            assert any(
                symptom_id in [symptom.id for symptom in med_book.symptoms]
                for symptom_id in symptom_ids
            )

    def test__fetch_by_symptoms__not_found(self, repo):
        # Call
        result = repo.fetch_by_symptoms([100])

        # Assert
        assert result == []


class TestFetchBySymptomsAndHelpedStatus:
    def test__helped_status_is_true(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, True
        )

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert all(review.is_helped for review in med_book.item_reviews) is True

    def test__helped_status_is_false(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, False
        )

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert all(review.is_helped for review in med_book.item_reviews) is False

    def test__order_by_rating_is_asc(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, True, order_by_rating='asc'
        )

        # Assert
        assert result is not None
        assert all(isinstance(med_book, entities.MedicalBook) for med_book in result)
        assert result == sorted(
            result, key=lambda med_book:
            sum(review.item_rating
                for review in med_book.item_reviews) / len(med_book.item_reviews),
            reverse=False
        )

    def test__order_by_rating_is_desc(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, True
        )

        # Assert
        assert result is not None
        assert all(isinstance(med_book, entities.MedicalBook) for med_book in result)
        assert result == sorted(
            result, key=lambda med_book:
            sum(review.item_rating
                for review in med_book.item_reviews) / len(med_book.item_reviews),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, True, limit=1
        )

        # Assert
        assert len(result) == 1

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        is_helped = True
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        med_books_by_symptoms: Sequence[entities.MedicalBook] = (
            session.query(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .filter(
                and_(
                    entities.MedicalBook.symptoms.any(
                        entities.Symptom.id.in_(symptom_ids)
                    ),
                    entities.ItemReview.is_helped == is_helped
                )
            )
            .order_by(desc(entities.ItemReview.item_rating))
            .all()
        )

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(
            symptom_ids, is_helped, offset=1
        )

        # Assert
        assert len(result) == len(med_books_by_symptoms) - 1
        assert med_books_by_symptoms[1:] == result


class TestFetchByDiagnosisAndHelpedStatus:
    def test__helped_status_is_true(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(diagnosis_id, True)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert all(review.is_helped for review in med_book.item_reviews) is True

    def test__helped_status_is_false(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(diagnosis_id, False)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert all(review.is_helped for review in med_book.item_reviews) is False

    def test__order_by_rating_is_asc(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id, True, 'asc'
        )

        # Assert
        assert result is not None
        assert all(isinstance(med_book, entities.MedicalBook) for med_book in result)
        assert result == sorted(
            result, key=lambda med_book:
            sum(review.item_rating
                for review in med_book.item_reviews) / len(med_book.item_reviews),
            reverse=False
        )

    def test__order_by_rating_is_desc(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id, True
        )

        # Assert
        assert result is not None
        assert all(isinstance(med_book, entities.MedicalBook) for med_book in result)
        assert result == sorted(
            result, key=lambda med_book:
            sum(review.item_rating
                for review in med_book.item_reviews) / len(med_book.item_reviews),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id, True, limit=1
        )

        # Assert
        assert len(result) == 1

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        is_helped = True
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        med_books_by_symptoms: Sequence[entities.MedicalBook] = (
            session.query(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .filter(
                and_(
                    entities.MedicalBook.diagnosis_id == diagnosis_id,
                    entities.ItemReview.is_helped == is_helped
                )
            )
            .order_by(desc(entities.ItemReview.item_rating))
            .all()
        )

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(
            diagnosis_id, True, offset=1
        )

        # Assert
        assert len(result) == len(med_books_by_symptoms) - 1
        assert med_books_by_symptoms[1:] == result


class TestAdd:
    def test__add(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())
        symptoms_to_add: list[entities.Symptom] = (
            session.query(entities.Symptom)
            .filter(
                entities.Symptom.id.in_(
                    [fill_db['symptom_ids'][0], fill_db['symptom_ids'][1]]
                )
            )
            .all()
        )
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
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
                symptoms=symptoms_to_add,
                item_reviews=reviews_to_add,
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)

    def test__add__with_no_symptoms(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())

        # Call
        result = repo.add(
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)

    def test__add__with_no_reviews(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())

        # Call
        result = repo.add(
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()

        # Call
        result = repo.remove(med_book)
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.MedicalBook)
