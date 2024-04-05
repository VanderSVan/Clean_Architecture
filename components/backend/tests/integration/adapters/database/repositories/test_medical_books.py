from itertools import product

import pytest
from sqlalchemy import select, func

from simple_medication_selection.adapters.database import tables, repositories
from simple_medication_selection.application import entities, dtos, schemas
from .. import test_data


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    patient_ids: list[int] = test_data.insert_patients(session)
    diagnosis_ids: list[int] = test_data.insert_diagnoses(session)
    symptom_ids: list[int] = test_data.insert_symptoms(session)
    category_ids: list[int] = test_data.insert_categories(session)
    type_ids: list[int] = test_data.insert_types(session)
    item_ids: list[int] = test_data.insert_items(type_ids, category_ids, session)
    review_ids: list[int] = test_data.insert_reviews(item_ids, session)
    med_book_ids: list[int] = test_data.insert_medical_books(patient_ids, diagnosis_ids,
                                                             session)
    test_data.insert_avg_rating(session)
    test_data.insert_medical_book_reviews(med_book_ids, review_ids, session)
    test_data.insert_medical_book_symptoms(med_book_ids, symptom_ids, session)
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


@pytest.fixture
def filter_params_factory(request, fill_db):
    """
    Фабрика параметров для фильтрации.
    """
    if 'patient_id' in request.param:
        new_params = schemas.FindPatientMedicalBooks(patient_id=fill_db['patient_ids'][0])
    else:
        new_params = schemas.FindMedicalBooks()

    for param, value in request.param.items():
        if param == 'symptom_ids':
            value = fill_db['symptom_ids']

        elif param == 'diagnosis_id':
            value = fill_db['diagnosis_ids'][0]

        elif param == 'patient_id':
            value = fill_db['patient_ids'][0]

        elif param == 'item_ids':
            value = fill_db['item_ids']

        setattr(new_params, param, value)

    return new_params


def combine_data(main: list[dict], mixin: list[dict]) -> list[dict]:
    """
    Комбинирует данные main и mixin
    """
    return [main_data | mixin_data for main_data, mixin_data in product(main, mixin)]


def pytest_generate_tests(metafunc):
    """
    Динамически генерирует параметры для тестов,
        только для тех которые имеют суффикс `Mixin`.
    """
    mixin_classes: tuple = (_TestOrderMixin,
                            _TestPaginationMixin,
                            _TestUniquenessMixin)

    for mixin_class in mixin_classes:
        if hasattr(mixin_class, metafunc.function.__name__):
            filter_params: list[dict] = PARAMS_TO_MIX[metafunc.cls.TEST_METHOD]
            mixin_params: list[dict] = PARAMS_TO_MIX[metafunc.function.__name__]
            combined_params: list[dict] = combine_data(main=filter_params,
                                                       mixin=mixin_params)
            metafunc.parametrize('filter_params_factory', combined_params, indirect=True)


PARAMS_TO_MIX: dict[str, list[dict]] = dict(
    fetch_all=[dict()],
    fetch_by_symptoms=[dict(symptom_ids=[1, 2, 3, 4])],
    fetch_by_matching_all_symptoms=[
        dict(symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_diagnosis=[dict(diagnosis_id=1)],
    fetch_by_diagnosis_and_symptoms=[dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4])],
    fetch_by_diagnosis_with_matching_all_symptoms=[
        dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_helped_status=[dict(is_helped=True), dict(is_helped=False)],
    fetch_by_helped_status_and_symptoms=[
        dict(is_helped=True, symptom_ids=[1, 2, 3, 4]),
        dict(is_helped=False, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_helped_status_with_matching_all_symptoms=[
        dict(is_helped=True, symptom_ids=[1, 2, 3, 4], match_all_symptoms=True),
        dict(is_helped=False, symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_helped_status_and_diagnosis=[
        dict(is_helped=True, diagnosis_id=1),
        dict(is_helped=False, diagnosis_id=1)
    ],
    fetch_by_helped_status_diagnosis_and_symptoms=[
        dict(is_helped=True, diagnosis_id=1, symptom_ids=[1, 2, 3, 4]),
        dict(is_helped=False, diagnosis_id=1, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_helped_status_diagnosis_with_matching_all_symptoms=[
        dict(is_helped=True, diagnosis_id=1, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True),
        dict(is_helped=False, diagnosis_id=1, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_patient=[dict(patient_id=1)],
    fetch_by_patient_and_symptoms=[dict(patient_id=1, symptom_ids=[1, 2, 3, 4])],
    fetch_by_patient_with_matching_all_symptoms=[
        dict(patient_id=1, symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_patient_and_helped_status=[
        dict(patient_id=1, is_helped=True),
        dict(patient_id=1, is_helped=False)
    ],
    fetch_by_patient_helped_status_and_symptoms=[
        dict(patient_id=1, is_helped=True, symptom_ids=[1, 2, 3, 4]),
        dict(patient_id=1, is_helped=False, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_helped_status_with_matching_all_symptoms=[
        dict(patient_id=1, is_helped=True, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True),
        dict(patient_id=1, is_helped=False, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_patient_helped_status_and_diagnosis=[
        dict(patient_id=1, is_helped=True, diagnosis_id=1),
        dict(patient_id=1, is_helped=False, diagnosis_id=1)
    ],
    fetch_by_patient_helped_status_diagnosis_and_symptoms=[
        dict(patient_id=1, is_helped=True, diagnosis_id=1, symptom_ids=[1, 2, 3, 4]),
        dict(patient_id=1, is_helped=False, diagnosis_id=1, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms=[
        dict(patient_id=1, is_helped=True, diagnosis_id=1, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True),
        dict(patient_id=1, is_helped=False, diagnosis_id=1, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_patient_diagnosis_with_matching_all_symptoms=[
        dict(patient_id=1, diagnosis_id=1, symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_patient_diagnosis_and_symptoms=[
        dict(patient_id=1, diagnosis_id=1, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_and_diagnosis=[dict(patient_id=1, diagnosis_id=1)],
    fetch_by_items=[dict(item_ids=[1, 2, 3, 4])],
    fetch_by_patient_and_items=[dict(patient_id=1, item_ids=[1, 2, 3, 4])],
    fetch_by_items_and_helped_status=[
        dict(item_ids=[1, 2, 3, 4], is_helped=True),
        dict(item_ids=[1, 2, 3, 4], is_helped=False)
    ],
    fetch_by_items_and_diagnosis=[dict(item_ids=[1, 2, 3, 4], diagnosis_id=1)],
    fetch_by_items_and_symptoms=[dict(item_ids=[1, 2, 3, 4], symptom_ids=[1, 2, 3, 4])],
    fetch_by_items_with_matching_all_symptoms=[
        dict(item_ids=[1, 2, 3, 4], symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_diagnosis_items_with_matching_all_symptoms=[
        dict(diagnosis_id=1, item_ids=[1, 2, 3, 4], symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_helped_status_items_with_matching_all_symptoms=[
        dict(is_helped=True, item_ids=[1, 2, 3, 4], symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True),
        dict(is_helped=False, item_ids=[1, 2, 3, 4], symptom_ids=[1, 2, 3, 4],
             match_all_symptoms=True)
    ],
    fetch_by_helped_status_diagnosis_and_items=[
        dict(is_helped=True, diagnosis_id=1, item_ids=[1, 2, 3, 4]),
        dict(is_helped=False, diagnosis_id=1, item_ids=[1, 2, 3, 4])
    ],
    fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms=[
        dict(is_helped=True, diagnosis_id=1, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True),
        dict(is_helped=False, diagnosis_id=1, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],

    fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms=[
        dict(patient_id=1, is_helped=True, diagnosis_id=1, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True),
        dict(patient_id=1, is_helped=False, diagnosis_id=1, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_patient_diagnosis_and_items=[
        dict(patient_id=1, diagnosis_id=1, item_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_diagnosis_items_with_matching_all_symptoms=[
        dict(patient_id=1, diagnosis_id=1, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_patient_helped_status_and_items=[
        dict(patient_id=1, is_helped=True, item_ids=[1, 2, 3, 4]),
        dict(patient_id=1, is_helped=False, item_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_helped_status_diagnosis_and_items=[
        dict(patient_id=1, is_helped=True, diagnosis_id=1, item_ids=[1, 2, 3, 4]),
        dict(patient_id=1, is_helped=False, diagnosis_id=1, item_ids=[1, 2, 3, 4])
    ],
    fetch_by_patient_helped_status_items_with_matching_all_symptoms=[
        dict(patient_id=1, is_helped=True, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True),
        dict(patient_id=1, is_helped=False, item_ids=[1, 2, 3, 4],
             symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],

    test__order_is_asc=[
        dict(sort_field='patient_id', sort_direction='asc'),
        dict(sort_field='diagnosis_id', sort_direction='asc'),
        dict(sort_field='title_history', sort_direction='asc')
    ],
    test__order_is_desc=[
        dict(sort_field='patient_id', sort_direction='desc'),
        dict(sort_field='diagnosis_id', sort_direction='desc'),
        dict(sort_field='title_history', sort_direction='desc')
    ],
    test__null_last=[dict()],
    test__with_limit=[dict(limit=1)],
    test__with_offset=[dict(offset=1)],
    test__unique_check=[dict()],
)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class _BaseMixin:
    TEST_METHOD: str


class _TestOrderMixin(_BaseMixin):

    def test__order_is_asc(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda med_book: (
                float('inf')
                if getattr(med_book, filter_params_factory.sort_field) is None
                else getattr(med_book, filter_params_factory.sort_field)
            ),
            reverse=False
        )

    def test__order_is_desc(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda med_book: (
                float('-inf')
                if getattr(med_book, filter_params_factory.sort_field) is None
                else getattr(med_book, filter_params_factory.sort_field)
            ),
            reverse=True
        )


class _TestPaginationMixin(_BaseMixin):

    def test__with_limit(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )
        # Assert
        assert len(result) == filter_params_factory.limit

    def test__with_offset(self, filter_params_factory, repo):
        # Call
        result_with_offset = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )

        filter_params_factory.offset = 0
        result_without_offset = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result_without_offset) > len(result_with_offset)


class _TestUniquenessMixin(_BaseMixin):

    def test__unique_check(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(set(result))


class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id(med_book.id)

        # Assert
        assert isinstance(result, dtos.MedicalBook)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id(1000000)

        # Assert
        assert result is None


class TestFetchByIdWithSymptoms:
    def test__fetch_by_id_with_symptoms(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id_with_symptoms(med_book.id)

        # Assert
        assert isinstance(result, dtos.MedicalBookWithSymptoms)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id_with_symptoms(1000000)

        # Assert
        assert result is None


class TestFetchByIdWithReviews:
    def test__fetch_by_id_with_reviews(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id_with_reviews(med_book.id)

        # Assert
        assert isinstance(result, dtos.MedicalBookWithItemReviews)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id_with_reviews(1000000)

        # Assert
        assert result is None


class TestFetchByIdWithSymptomsAndReviews:
    def test__fetch_by_id_with_symptoms_and_reviews(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id_with_symptoms_and_reviews(med_book.id)

        # Assert
        assert isinstance(result, entities.MedicalBook)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id_with_symptoms_and_reviews(1000000)

        # Assert
        assert result is None


class TestFetchAll(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'

    def test__fetch_all(self, repo, session):
        # Setup
        filter_params = schemas.FindMedicalBooks()

        # Call
        result = repo.fetch_all(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBook)


class TestFetchBySymptoms(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms'

    def test__fetch_by_symptoms(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        filter_params = schemas.FindMedicalBooks(symptom_ids=symptom_ids)

        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBookWithSymptoms)
            assert fetched_med_book.id in expected_med_book_ids
            fetched_med_book_symptom_ids: list[int] = [
                symptom.id for symptom in fetched_med_book.symptoms
            ]
            assert any(symptom_id in fetched_med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByMatchingAllSymptoms(_TestOrderMixin,
                                     _TestPaginationMixin,
                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_matching_all_symptoms'

    def test__fetch_by_matching_all_symptoms(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        filter_params = schemas.FindMedicalBooks(match_all_symptoms=True,
                                                 symptom_ids=symptom_ids)

        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_matching_all_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBookWithSymptoms)
            assert fetched_med_book.id in expected_med_book_ids
            fetched_med_book_symptom_ids: list[int] = [
                symptom.id for symptom in fetched_med_book.symptoms
            ]
            assert all(symptom_id in fetched_med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByDiagnosis(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis'

    def test__fetch_by_diagnosis(self, repo, session, fill_db):
        filter_params = schemas.FindMedicalBooks(
            diagnosis_id=fill_db['diagnosis_ids'][0]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id


class TestFetchByDiagnosisAndSymptoms(_TestOrderMixin,
                                      _TestPaginationMixin,
                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_symptoms'

    def test__fetch_by_diagnosis_and_symptoms(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithSymptoms)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                  _TestPaginationMixin,
                                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_with_matching_all_symptoms'

    def test__fetch_by_diagnosis_with_matching_all_symptoms(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithSymptoms)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatus(_TestOrderMixin,
                              _TestPaginationMixin,
                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status'

    @pytest.mark.parametrize('helped_status', [True, False, ])
    def test__fetch_by_helped_status(self, helped_status, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(is_helped=helped_status)
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert helped_status in [review.is_helped for review in med_book.item_reviews]


class TestFetchByHelpedStatusAndSymptoms(_TestOrderMixin,
                                         _TestPaginationMixin,
                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_and_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_and_symptoms(self, helped_status, repo, session,
                                                  fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            symptom_ids=fill_db['symptom_ids'],
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_and_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatusWithMatchingAllSymptoms(_TestOrderMixin,
                                                     _TestPaginationMixin,
                                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_with_matching_all_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_with_matching_all_symptoms(self, helped_status,
                                                                repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            symptom_ids=fill_db['symptom_ids'],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatusAndDiagnosis(_TestOrderMixin,
                                          _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_and_diagnosis'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_and_diagnosis(self, helped_status, repo, session,
                                                   fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_and_diagnosis(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]


class TestFetchByHelpedStatusDiagnosisAndSymptoms(_TestOrderMixin,
                                                  _TestPaginationMixin,
                                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_and_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_diagnosis_and_symptoms(self, helped_status, repo,
                                                            session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_diagnosis_and_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatusDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                              _TestPaginationMixin,
                                                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatient(_TestOrderMixin,
                         _TestPaginationMixin,
                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient'

    def test__fetch_by_patient(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(patient_id=med_book.patient_id)

        # Call
        result = repo.fetch_by_patient(filter_params=filter_params)

        # Assert
        assert result is not None
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBook)
            assert fetched_med_book.patient_id == med_book.patient_id


class TestFetchByPatientAndSymptoms(_TestOrderMixin,
                                    _TestPaginationMixin,
                                    _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_symptoms'

    def test__fetch_by_patient_and_symptoms(self, repo, session, fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        filter_params = schemas.FindPatientMedicalBooks(patient_id=med_book.patient_id,
                                                        symptom_ids=symptom_ids)
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBookWithSymptoms)
            assert fetched_med_book.patient_id == med_book.patient_id
            fetched_med_book_symptom_ids: list[int] = [
                symptom.id for symptom in fetched_med_book.symptoms
            ]
            assert all(symptom_id in fetched_med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientWithMatchingAllSymptoms(_TestOrderMixin,
                                                _TestPaginationMixin,
                                                _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_with_matching_all_symptoms'

    def test__fetch_by_patient_matching_all_symptoms(self, repo,
                                                     session, fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        symptom_ids: list[int] = fill_db['symptom_ids']
        filter_params = schemas.FindPatientMedicalBooks(patient_id=med_book.patient_id,
                                                        symptom_ids=symptom_ids,
                                                        match_all_symptoms=True)
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, dtos.MedicalBookWithSymptoms)
            assert fetched_med_book.patient_id == med_book.patient_id
            assert len(fetched_med_book.symptoms) >= len(filter_params.symptom_ids)
            fetched_med_book_symptom_ids: list[int] = [
                symptom.id for symptom in fetched_med_book.symptoms
            ]
            assert len(fetched_med_book_symptom_ids) >= len(filter_params.symptom_ids)
            assert all(symptom_id in fetched_med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientAndHelpedStatus(_TestOrderMixin,
                                        _TestPaginationMixin,
                                        _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_helped_status'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_and_helped_status(self, helped_status, repo, session,
                                                 fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(patient_id=med_book.patient_id,
                                                        is_helped=helped_status)
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_helped_status(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]


class TestFetchByPatientHelpedStatusAndSymptoms(_TestOrderMixin,
                                                _TestPaginationMixin,
                                                _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_and_symptoms(self, helped_status, repo,
                                                          session, fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=med_book.patient_id,
            is_helped=helped_status,
            symptom_ids=fill_db['symptom_ids']
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_and_symptoms(
            filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientHelpedStatusWithMatchingAllSymptoms(_TestOrderMixin,
                                                            _TestPaginationMixin,
                                                            _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_with_matching_all_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_and_symptoms(self, helped_status, repo,
                                                          session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            is_helped=helped_status,
            symptom_ids=fill_db['symptom_ids'][:2],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientHelpedStatusAndDiagnosis(_TestOrderMixin,
                                                 _TestPaginationMixin,
                                                 _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_diagnosis'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_and_diagnosis(self, helped_status, repo,
                                                           session, fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=med_book.patient_id,
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_and_diagnosis(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]


class TestFetchByPatientHelpedStatusDiagnosisAndSymptoms(_TestOrderMixin,
                                                         _TestPaginationMixin,
                                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_and_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_diagnosis_and_symptoms(self, helped_status,
                                                                    repo, session,
                                                                    fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=med_book.patient_id,
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_diagnosis_and_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientHelpedStatusDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                                     _TestPaginationMixin,
                                                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=med_book.patient_id,
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2],
            match_all_symptoms=True
        )

        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert helped_status in [review.is_helped for review in med_book.item_reviews]
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                         _TestPaginationMixin,
                                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_with_matching_all_symptoms'

    def test__fetch_by_patient_diagnosis_with_matching_all_symptoms(self, repo,
                                                                    session,
                                                                    fill_db):
        # Setup
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=med_book.patient_id,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_diagnosis_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithSymptoms)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientDiagnosisAndSymptoms(_TestOrderMixin,
                                             _TestPaginationMixin,
                                             _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_and_symptoms'

    def test__fetch_by_patient_diagnosis_and_symptoms(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            diagnosis_id=fill_db['diagnosis_ids'][0],
            symptom_ids=fill_db['symptom_ids'][:2]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_diagnosis_and_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientAndDiagnosis(_TestOrderMixin,
                                     _TestPaginationMixin,
                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_diagnosis'

    def test__fetch_by_patient_and_diagnosis(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            diagnosis_id=fill_db['diagnosis_ids'][0]
        )
        query = (
            select(entities.MedicalBook.id)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_diagnosis(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id


class TestFetchByItems(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items'

    def test__fetch_by_items(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            item_ids=[fill_db['item_ids'][0], fill_db['item_ids'][1]]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)


class TestFetchByPatientAndItems(_TestOrderMixin,
                                 _TestPaginationMixin,
                                 _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_items'

    def test__fetch_by_patient_and_items(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            item_ids=[fill_db['item_ids'][0], fill_db['item_ids'][1]]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_items(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == med_book.patient_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)


class TestFetchByItemsAndHelpedStatus(_TestOrderMixin,
                                      _TestPaginationMixin,
                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_helped_status'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_items_and_helped_status(self, helped_status, repo, session,
                                               fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            item_ids=[fill_db['item_ids'][0], fill_db['item_ids'][1]],
            is_helped=helped_status
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_and_helped_status(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)


class TestFetchByItemsAndDiagnosis(_TestOrderMixin,
                                   _TestPaginationMixin,
                                   _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_diagnosis'

    def test__fetch_by_items_and_diagnosis(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            item_ids=[*fill_db['item_ids']],
            diagnosis_id=fill_db['diagnosis_ids'][0]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_and_diagnosis(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)


class TestFetchByItemsAndSymptoms(_TestOrderMixin,
                                  _TestPaginationMixin,
                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_symptoms'

    def test__fetch_by_items_and_symptoms(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids']]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_and_symptoms(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert any(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                              _TestPaginationMixin,
                                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_with_matching_all_symptoms'

    def test__fetch_by_items_with_matching_all_symptoms(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByDiagnosisItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                                       _TestPaginationMixin,
                                                       _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_items_with_matching_all_symptoms'

    def test__fetch_by_diagnosis_items_with_matching_all_symptoms(self, repo, session,
                                                                  fill_db):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_items_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatusItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                                          _TestPaginationMixin,
                                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_items_with_matching_all_symptoms'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_items_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_items_with_matching_all_symptoms(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByHelpedStatusDiagnosisAndItems(_TestOrderMixin,
                                               _TestPaginationMixin,
                                               _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_and_items'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_diagnosis_and_items(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            item_ids=[*fill_db['item_ids']],
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_diagnosis_and_items(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)


class TestFetchByHelpedStatusDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = (
        'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'
    )

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            diagnosis_id=fill_db['diagnosis_ids'][0],
            is_helped=helped_status,
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = (
            repo
            .fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
                filter_params=filter_params
            )
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientDiagnosisAndItems(_TestOrderMixin,
                                          _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_and_items'

    def test__fetch_by_patient_diagnosis_and_items(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            diagnosis_id=fill_db['diagnosis_ids'][0],
            item_ids=[*fill_db['item_ids']]
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_diagnosis_and_items(filter_params=filter_params)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)


class TestFetchByPatientDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = 'fetch_by_patient_diagnosis_items_with_matching_all_symptoms'

    def test__fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
        self, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            diagnosis_id=fill_db['diagnosis_ids'][0],
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = (
            repo
            .fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
                filter_params=filter_params
            )
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientHelpedStatusAndItems(_TestOrderMixin,
                                             _TestPaginationMixin,
                                             _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_items'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_and_items(self, helped_status, repo, session,
                                                       fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            is_helped=helped_status,
            item_ids=[*fill_db['item_ids']],
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_and_items(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)


class TestFetchByPatientHelpedStatusDiagnosisAndItems(_TestOrderMixin,
                                                      _TestPaginationMixin,
                                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_and_items'

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_diagnosis_and_items(
        self, helped_status, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            is_helped=helped_status,
            diagnosis_id=fill_db['diagnosis_ids'][0],
            item_ids=[*fill_db['item_ids']],
        )
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_helped_status_diagnosis_and_items(
            filter_params=filter_params
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookWithItemReviews)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)


class TestFetchByPatientHelpedStatusItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = (
        'fetch_by_patient_helped_status_items_with_matching_all_symptoms'
    )

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_items_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            is_helped=helped_status,
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = (
            repo
            .fetch_by_patient_helped_status_items_with_matching_all_symptoms(
                filter_params=filter_params
            )
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


class TestFetchByPatientHelpedStatusDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = (
        'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'
    )

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
        self, helped_status, repo, session, fill_db
    ):
        # Setup
        filter_params = schemas.FindPatientMedicalBooks(
            patient_id=fill_db['patient_ids'][0],
            diagnosis_id=fill_db['diagnosis_ids'][0],
            is_helped=helped_status,
            item_ids=[*fill_db['item_ids']],
            symptom_ids=[*fill_db['symptom_ids'][:2]],
            match_all_symptoms=True
        )
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(filter_params.symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = (
            repo
            .fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
                filter_params=filter_params
            )
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id
            assert med_book.diagnosis_id == filter_params.diagnosis_id
            assert len(med_book.symptoms) >= len(filter_params.symptom_ids)
            assert any(review.item_id in filter_params.item_ids
                       for review in med_book.item_reviews)
            assert any(review.is_helped == filter_params.is_helped
                       for review in med_book.item_reviews)
            med_book_symptom_ids: list[int] = [
                symptom.id for symptom in med_book.symptoms
            ]
            assert all(symptom_id in med_book_symptom_ids
                       for symptom_id in filter_params.symptom_ids)


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
