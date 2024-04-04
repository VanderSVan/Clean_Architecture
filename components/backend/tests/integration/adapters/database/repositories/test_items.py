from itertools import product
from typing import Sequence

import pytest
from sqlalchemy import select, func

from simple_medication_selection.adapters.database import repositories
from simple_medication_selection.application import entities, dtos, schemas

from .. import test_data
from ..conftest import session


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
    return repositories.TreatmentItemsRepo(context=transaction_context)


@pytest.fixture
def filter_params_factory(request, fill_db):
    """
    Фабрика параметров для фильтрации.
    """
    new_params = schemas.FindTreatmentItems()

    for param, value in request.param.items():
        if param == 'symptom_ids':
            value = fill_db['symptom_ids']

        elif param == 'diagnosis_id':
            value = fill_db['diagnosis_ids'][0]

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
                            _TestNullsLastMixin,
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
    fetch_by_helped_status=[dict(is_helped=True), dict(is_helped=False)],
    fetch_by_symptoms=[
        dict(symptom_ids=[1, 2, 3, 4], match_all_symptoms=True),
        dict(symptom_ids=[1, 2, 3, 4], match_all_symptoms=False)
    ],
    fetch_by_diagnosis=[dict(diagnosis_id=1)],
    fetch_by_symptoms_and_helped_status=[
        dict(is_helped=True, match_all_symptoms=True, symptom_ids=[1, 2, 3, 4]),
        dict(is_helped=False, match_all_symptoms=False, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_diagnosis_and_helped_status=[
        dict(is_helped=True, diagnosis_id=1, symptom_ids=[1, 2, 3, 4]),
        dict(is_helped=False, diagnosis_id=1, symptom_ids=[1, 2, 3, 4])
    ],
    fetch_by_diagnosis_and_symptoms=[
        dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4], match_all_symptoms=False),
        dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4], match_all_symptoms=True)
    ],
    fetch_by_helped_status_diagnosis_symptoms=[
        dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4], is_helped=True,
             match_all_symptoms=True),
        dict(diagnosis_id=1, symptom_ids=[1, 2, 3, 4], is_helped=False,
             match_all_symptoms=False)
    ],
    test__order_is_asc=[
        dict(sort_field='title', sort_direction='asc'),
        dict(sort_field='price', sort_direction='asc'),
        dict(sort_field='avg_rating', sort_direction='asc')
    ],
    test__order_is_desc=[
        dict(sort_field='title', sort_direction='desc'),
        dict(sort_field='price', sort_direction='desc'),
        dict(sort_field='avg_rating', sort_direction='desc')
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
    TEST_ARGS: tuple = tuple()
    TEST_KWARGS: dict = dict()


class _TestOrderMixin(_BaseMixin):

    def test__order_is_asc(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('inf')
                if getattr(treatment_item, filter_params_factory.sort_field) is None
                else getattr(treatment_item, filter_params_factory.sort_field)
            ),
            reverse=False
        )

    def test__order_is_desc(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda treatment_item: (
                float('-inf')
                if getattr(treatment_item, filter_params_factory.sort_field) is None
                else getattr(treatment_item, filter_params_factory.sort_field)
            ),
            reverse=True
        )


class _TestNullsLastMixin(_BaseMixin):

    def test__null_last(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None


class _TestPaginationMixin(_BaseMixin):

    def test__with_limit(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) == filter_params_factory.limit

    def test__with_offset(self, filter_params_factory, repo):
        # Call
        result_with_offset = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        filter_params_factory.offset = 0
        result_without_offset = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result_without_offset) > len(result_with_offset)


class _TestUniquenessMixin(_BaseMixin):

    def test__unique_check(self, filter_params_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(
            *self.TEST_ARGS if self.TEST_ARGS else [],
            **self.TEST_KWARGS if self.TEST_KWARGS else {},
            filter_params=filter_params_factory
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(set(result))


class TestFetchById:
    def test__fetch_by_id(self, repo, session, fill_db):
        # Setup
        expected_item_id: int = fill_db['item_ids'][0]

        # Call
        result = repo.fetch_by_id(expected_item_id, False)

        # Assert
        assert isinstance(result, dtos.TreatmentItem)
        assert result.id == expected_item_id

    def test__item_not_found(self, repo, session, fill_db):
        # Setup
        expected_item_id: int = max(fill_db['item_ids']) + 1

        # Call
        result = repo.fetch_by_id(expected_item_id, False)

        # Assert
        assert result is None


class TestFetchByIdWithReviews:
    def test__fetch_by_id(self, repo, session, fill_db):
        # Setup
        expected_item_id: int = fill_db['item_ids'][0]

        # Call
        result = repo.fetch_by_id(expected_item_id, True)

        # Assert
        assert isinstance(result, entities.TreatmentItem)
        assert result.id == expected_item_id
        assert len(result.reviews) > 0

    def test__item_not_found(self, repo, session, fill_db):
        # Setup
        expected_item_id: int = max(fill_db['item_ids']) + 1

        # Call
        result = repo.fetch_by_id(expected_item_id, True)

        # Assert
        assert result is None


class TestFetchAll(_TestOrderMixin,
                   _TestNullsLastMixin,
                   _TestPaginationMixin,
                   _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = dict(with_reviews=False)

    def test__fetch_all(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindTreatmentItems()

        # Call
        result = repo.fetch_all(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(test_data.ITEMS_DATA)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)


class TestFetchAllWithReviews(_TestOrderMixin,
                              _TestNullsLastMixin,
                              _TestPaginationMixin,
                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = dict(with_reviews=True)

    def test__fetch_all_with_reviews(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindTreatmentItems()

        # Call
        result = repo.fetch_all(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(test_data.ITEMS_DATA)
        assert all(isinstance(item, entities.TreatmentItem) for item in result)
        assert any(len(item.reviews) > 0 for item in result)


class TestFetchByHelpedStatus(_TestOrderMixin,
                              _TestPaginationMixin,
                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status(self, helped_status, repo, session, fill_db):
        # Setup
        expected_item_ids: list[int] = (
            session.execute(
                select(entities.TreatmentItem.id)
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == helped_status)
                .distinct(entities.TreatmentItem.id)
            ).scalars().all()
        )
        filter_params = schemas.FindTreatmentItems(is_helped=helped_status)

        # Call
        result = repo.fetch_by_helped_status(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByHelpedStatusWithReviews(_TestOrderMixin,
                                         _TestPaginationMixin,
                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_helped_status(self, helped_status, repo, session, fill_db):
        # Setup
        expected_item_ids: list[int] = (
            session.execute(
                select(entities.TreatmentItem.id)
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == helped_status)
                .distinct(entities.TreatmentItem.id)
            ).scalars().all()
        )
        filter_params = schemas.FindTreatmentItems(is_helped=helped_status)

        # Call
        result = repo.fetch_by_helped_status(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptoms(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('match_all_symptoms', [True, False])
    def test__fetch_by_symptoms(self, match_all_symptoms, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptomsWithReviews(_TestOrderMixin, _TestPaginationMixin,
                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('match_all_symptoms', [True, False])
    def test__fetch_by_symptoms(self, match_all_symptoms, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosis(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis'
    TEST_KWARGS = dict(with_reviews=False)

    def test__fetch_by_diagnosis(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][2]
        expected_item_ids: list[int] = (
            session.execute(
                select(entities.ItemReview.item_id)
                .join(entities.MedicalBook.item_reviews)
                .where(entities.MedicalBook.diagnosis_id == diagnosis_id)
                .distinct(entities.ItemReview.item_id)
            ).scalars().all()
        )
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id)

        # Call
        result = repo.fetch_by_diagnosis(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisWithReviews(_TestOrderMixin, _TestPaginationMixin,
                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis'
    TEST_KWARGS = dict(with_reviews=True)

    def test__fetch_by_diagnosis_with_reviews(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        expected_item_ids: list[int] = (
            session.execute(
                select(entities.ItemReview.item_id)
                .join(entities.MedicalBook.item_reviews)
                .where(entities.MedicalBook.diagnosis_id == diagnosis_id)
                .distinct(entities.ItemReview.item_id)
            ).scalars().all()
        )
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id)

        # Call
        result = repo.fetch_by_diagnosis(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptomsAndHelpedStatus(_TestOrderMixin, _TestPaginationMixin,
                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms_and_helped_status'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('helped_status, match_all_symptoms', [
        (True, True),
        (False, False),
        (True, False),
        (False, True),
    ])
    def test__fetch_by_symptoms_and_helped_status(self, helped_status, match_all_symptoms,
                                                  repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][1:2]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptomsAndHelpedStatusWithReviews(_TestOrderMixin,
                                                    _TestPaginationMixin,
                                                    _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms_and_helped_status'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('helped_status, match_all_symptoms', [
        (True, True),
        (False, False),
        (True, False),
        (False, True),
    ])
    def test__fetch_by_symptoms_and_helped_status(self, helped_status, match_all_symptoms,
                                                  repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][1:2]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisAndHelpedStatus(_TestOrderMixin, _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_helped_status'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_diagnosis_and_helped_status(self, helped_status, repo, session,
                                                   fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.MedicalBook.diagnosis_id == diagnosis_id)
            .group_by(entities.ItemReview.item_id)
        )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisAndHelpedStatusWithReviews(_TestOrderMixin,
                                                     _TestPaginationMixin,
                                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_helped_status'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('helped_status', [True, False])
    def test__fetch_by_diagnosis_and_helped_status(self, helped_status, repo, session,
                                                   fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.MedicalBook.diagnosis_id == diagnosis_id)
            .group_by(entities.ItemReview.item_id)
        )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisSymptoms(_TestOrderMixin,
                                   _TestPaginationMixin,
                                   _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_symptoms'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('match_all_symptoms', [True, False])
    def test__fetch_by_diagnosis_and_symptoms(self, match_all_symptoms, repo, session,
                                              fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        symptom_ids: list[int] = fill_db['symptom_ids']
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id,
                                                   symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_symptoms(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisSymptomsWithReviews(_TestOrderMixin,
                                              _TestPaginationMixin,
                                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_symptoms'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('match_all_symptoms', [True, False])
    def test__fetch_by_diagnosis_and_symptoms_with_reviews(self, match_all_symptoms, repo,
                                                           session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        symptom_ids: list[int] = fill_db['symptom_ids']
        filter_params = schemas.FindTreatmentItems(diagnosis_id=diagnosis_id,
                                                   symptom_ids=symptom_ids,
                                                   match_all_symptoms=match_all_symptoms)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_symptoms(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByHelpedStatusDiagnosisSymptoms(_TestOrderMixin,
                                               _TestPaginationMixin,
                                               _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_symptoms'
    TEST_KWARGS = dict(with_reviews=False)

    @pytest.mark.parametrize('helped_status, match_all_symptoms', [
        (True, True),
        (False, False),
        (True, False),
        (False, True),
    ])
    def test__fetch_by_helped_status_diagnosis_symptoms(self, helped_status,
                                                        match_all_symptoms, repo, session,
                                                        fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][1]
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   diagnosis_id=diagnosis_id,
                                                   match_all_symptoms=match_all_symptoms,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_diagnosis_symptoms(filter_params, False)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, dtos.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByHelpedStatusDiagnosisSymptomsWithReviews(_TestOrderMixin,
                                                          _TestPaginationMixin,
                                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_symptoms'
    TEST_KWARGS = dict(with_reviews=True)

    @pytest.mark.parametrize('helped_status, match_all_symptoms', [
        (True, True),
        (False, False),
        (True, False),
        (False, True),
    ])
    def test__fetch_by_helped_status_diagnosis_symptoms(self, helped_status,
                                                        match_all_symptoms, repo, session,
                                                        fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][1]
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        filter_params = schemas.FindTreatmentItems(symptom_ids=symptom_ids,
                                                   diagnosis_id=diagnosis_id,
                                                   match_all_symptoms=match_all_symptoms,
                                                   is_helped=helped_status)
        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if match_all_symptoms:
            query = (query
                     .having(func.count(entities.Symptom.id.distinct()) ==
                             len(symptom_ids))
                     )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_diagnosis_symptoms(filter_params, True)

        # Assert
        assert isinstance(result, Sequence)
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        assert any(len(item.reviews) > 0 for item in result)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestAdd:
    def test__add(self, repo, session, fill_db):
        # Setup
        before_count = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
        )

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
        after_count = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
        )

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.TreatmentItem)

    def test__add_with_reviews(self, repo, session, fill_db):
        # Setup
        before_count = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
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
            entities.TreatmentItem(
                title='Title 1',
                price=1000.50,
                description='Description 1',
                category_id=fill_db['category_ids'][0],
                type_id=fill_db['type_ids'][0],
                reviews=reviews_to_add
            )
        )
        after_count = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
        )

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.TreatmentItem)

    def test__cascade_update_reviews(self, repo, session, fill_db):
        # Setup
        existing_item: entities.TreatmentItem = session.execute(
            select(entities.TreatmentItem)
            .join(entities.TreatmentItem.reviews)
            .where(entities.TreatmentItem.reviews is not None)
        ).scalar()

        # Assert
        assert len(existing_item.reviews) > 0
        for review in existing_item.reviews:
            review.item_id = existing_item.id

        # Call
        existing_item.id = (
            session.execute(func.max(entities.TreatmentItem.id)).scalar() + 1
        )

        # Setup
        updated_item: entities.TreatmentItem = session.execute(
            select(entities.TreatmentItem)
            .where(entities.TreatmentItem.id == existing_item.id)
        ).scalar()

        # Assert
        assert len(updated_item.reviews) > 0
        for updated_review in updated_item.reviews:
            assert updated_review.item_id == updated_item.id


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count: int = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
        )
        item_to_remove: entities.TreatmentItem = (
            session.query(entities.TreatmentItem).first()
        )

        # Call
        result = repo.remove(item_to_remove)

        # Setup
        after_count: int = len(
            session.execute(select(entities.TreatmentItem)).scalars().all()
        )

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.TreatmentItem)

    def test__cascade_delete_reviews(self, repo, session, fill_db):
        # Setup
        item_to_remove: entities.TreatmentItem = (
            session.execute(
                select(entities.TreatmentItem)
                .join(entities.TreatmentItem.reviews)
                .where(entities.TreatmentItem.reviews is not None)
            ).scalar()
        )
        orphaned_review_ids: list[int] = [review.id for review in item_to_remove.reviews]

        # Assert
        assert len(orphaned_review_ids) > 0

        # Call
        repo.remove(item_to_remove)

        # Setup
        reviews_after_remove: list[entities.ItemReview] = (
            session.execute(select(entities.ItemReview.id)).scalars().all()
        )

        # Assert
        assert len(reviews_after_remove) > 0
        for review_id in orphaned_review_ids:
            assert review_id not in reviews_after_remove
