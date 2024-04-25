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
def kwargs_factory(request, fill_db) -> dict[str, bool | schemas.FindTreatmentItems]:
    """
    Fixture для обновления аргументов теста с корректными идентификаторами (id) при
    необходимости.

    Область работы сессии настроена на функцию, и после `rollback` идентификаторы
    сохраняют инкрементированное значение из-за `autoincrement=True`. Эта фикстура
    гарантирует, что аргументы теста всегда будут содержать корректные идентификаторы.

    :param request: Объект _pytest.fixtures.SubRequest, содержащий параметры теста.
    :param fill_db: Словарь с заполненными данными, используемыми для обновления
        аргументов.
    :return: Обновленный словарь с аргументами теста.
    """
    filter_params = request.param['filter_params']

    params_to_change = {
        'symptom_ids': fill_db['symptom_ids'],
        'diagnosis_id': fill_db['diagnosis_ids'][0],
    }

    for param, value in filter_params:
        if value is None:
            continue
        setattr(filter_params, param, params_to_change.get(param, value))

    request.param['filter_params'] = filter_params

    return request.param


def _combine_data(main: list[dict], mixin: list[dict]) -> list[dict]:
    """
    Комбинирует данные main и mixin
    """
    combined_data: list[dict[str, bool | schemas.FindTreatmentItems]] = []
    for main_data, mixin_data in product(main, mixin):

        if 'filter_params' not in main_data or 'filter_params' not in mixin_data:
            raise KeyError(f"`filter_params` not found in `{main_data=}`. "
                           f"Check your test and parametrize data.")

        main_filter_params_class = main_data['filter_params'].__class__
        if not (isinstance(main_data['filter_params'], schemas.FindTreatmentItems)):
            raise TypeError(f"Expected `filter_params` to be an instance of "
                            f"`{schemas.FindTreatmentItems.__name__}`, "
                            f"got `{main_filter_params_class.__name__}`.")

        main_filter_params: dict = main_data['filter_params'].__dict__
        mixin_filter_params: dict = mixin_data['filter_params'].__dict__

        # Миксует данные из `main_filter_params` и `mixin_filter_params`,
        # создавая новый экземпляр `new_main_filter_params`.
        new_main_filter_params = main_filter_params_class(**main_filter_params)
        for key, value in mixin_filter_params.items():
            if value is not None:
                setattr(new_main_filter_params, key, value)

        combined_data.append({
            'include_reviews': main_data['include_reviews'],
            'filter_params': new_main_filter_params
        })

    return combined_data


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
        func_name: str = metafunc.function.__name__
        if hasattr(mixin_class, func_name):
            method_kwargs: list[dict] = metafunc.cls.TEST_KWARGS
            mixin_kwargs: list[dict] = metafunc.cls.MIXIN_KWARGS[func_name]
            combined_kwargs: list[dict] = _combine_data(main=method_kwargs,
                                                        mixin=mixin_kwargs)
            metafunc.parametrize('kwargs_factory', combined_kwargs, indirect=True)


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
    TEST_KWARGS: list[dict]
    MIXIN_KWARGS: dict[str, list[dict]] = dict(
        test__order_is_asc=[
            dict(filter_params=schemas.FindTreatmentItems(sort_field='title',
                                                             sort_direction='asc')),
            dict(filter_params=schemas.FindTreatmentItems(sort_field='price',
                                                             sort_direction='asc')),
            dict(filter_params=schemas.FindTreatmentItems(sort_field='avg_rating',
                                                             sort_direction='asc'))
        ],
        test__order_is_desc=[
            dict(filter_params=schemas.FindTreatmentItems(sort_field='title',
                                                             sort_direction='desc')),
            dict(filter_params=schemas.FindTreatmentItems(sort_field='price',
                                                             sort_direction='desc')),
            dict(filter_params=schemas.FindTreatmentItems(sort_field='avg_rating',
                                                             sort_direction='desc'))
        ],
        test__with_limit=[dict(filter_params=schemas.FindTreatmentItems(limit=1))],
        test__with_offset=[dict(filter_params=schemas.FindTreatmentItems(offset=1))],
        test__unique_check=[dict(filter_params=schemas.FindTreatmentItems())],
        test__null_last=[dict(filter_params=schemas.FindTreatmentItems())],
    )


class _TestOrderMixin(_BaseMixin):

    def test__order_is_asc(self, kwargs_factory, repo):
        # Setup
        filter_params = kwargs_factory['filter_params']

        # Call
        result = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda med_book: (
                float('inf')
                if getattr(med_book, filter_params.sort_field) is None
                else getattr(med_book, filter_params.sort_field)
            ),
            reverse=False
        )

    def test__order_is_desc(self, kwargs_factory, repo):
        # Setup
        filter_params = kwargs_factory['filter_params']

        # Call
        result = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda med_book: (
                float('-inf')
                if getattr(med_book, filter_params.sort_field) is None
                else getattr(med_book, filter_params.sort_field)
            ),
            reverse=True
        )


class _TestPaginationMixin(_BaseMixin):

    def test__with_limit(self, kwargs_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result) == kwargs_factory['filter_params'].limit

    def test__with_offset(self, kwargs_factory, repo):
        # Setup
        offset = kwargs_factory['filter_params'].offset
        filter_params = kwargs_factory['filter_params']

        # Call
        result_with_offset = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Setup
        new_filter_params = filter_params.__class__(**filter_params.__dict__)
        new_filter_params.offset = 0

        kwargs_factory['filter_params'] = new_filter_params
        result_without_offset = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result_without_offset) > len(result_with_offset)
        assert len(result_with_offset) == len(result_without_offset) - offset


class _TestUniquenessMixin(_BaseMixin):

    def test__unique_check(self, kwargs_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result) > 0
        assert len(result) == len(set(result))


class _TestNullsLastMixin(_BaseMixin):

    def test__null_last(self, kwargs_factory, repo):
        # Call
        result = getattr(repo, self.TEST_METHOD)(**kwargs_factory)

        # Assert
        assert len(result) > 0
        assert result[0].avg_rating is not None
        assert result[-1].avg_rating is None


class TestFetchById:
    def test__fetch_by_id(self, repo, session, fill_db):
        # Setup
        expected_item_id: int = fill_db['item_ids'][0]

        # Call
        result = repo.fetch_by_id(expected_item_id, False)

        # Assert
        assert isinstance(result, entities.TreatmentItem)
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
                   _TestPaginationMixin,
                   _TestUniquenessMixin,
                   _TestNullsLastMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False, filter_params=schemas.FindTreatmentItems()),
        dict(include_reviews=True, filter_params=schemas.FindTreatmentItems())
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_all(self, kwargs, repo, session, fill_db):
        # Call
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(test_data.ITEMS_DATA)
        assert all(isinstance(item, entities.TreatmentItem) for item in result)


class TestFetchByHelpedStatus(_TestOrderMixin,
                              _TestPaginationMixin,
                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(is_helped=True)),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(is_helped=False)),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(is_helped=True)),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(is_helped=False))
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        helped_status = kwargs['filter_params'].is_helped
        expected_item_ids: list[int] = (
            session.execute(
                select(entities.TreatmentItem.id)
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == helped_status)
                .distinct(entities.TreatmentItem.id)
            ).scalars().all()
        )

        # Call
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptoms(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False)
             ),
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        match_all_symptoms: bool = kwargs['filter_params'].match_all_symptoms
        kwargs['filter_params'].symptom_ids = symptom_ids

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
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosis(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(diagnosis_id=1)),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(diagnosis_id=1))
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_diagnosis(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].diagnosis_id = diagnosis_id

        expected_item_ids: list[int] = (
            session.execute(
                select(entities.ItemReview.item_id)
                .join(entities.MedicalBook.item_reviews)
                .where(entities.MedicalBook.diagnosis_id == diagnosis_id)
                .distinct(entities.ItemReview.item_id)
            ).scalars().all()
        )

        # Call
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchBySymptomsAndHelpedStatus(_TestOrderMixin, _TestPaginationMixin,
                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=True)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=False)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=True)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=False)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=True)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=False)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=True)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=False)
             ),
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_symptoms_and_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        symptom_ids = fill_db['symptom_ids'][:2]
        helped_status = kwargs['filter_params'].is_helped
        match_all_symptoms = kwargs['filter_params'].match_all_symptoms
        kwargs['filter_params'].symptom_ids = symptom_ids

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
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisAndHelpedStatus(_TestOrderMixin, _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, is_helped=True)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, is_helped=False)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, is_helped=True)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, is_helped=False)
             ),
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_diagnosis_and_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        helped_status = kwargs['filter_params'].is_helped
        kwargs['filter_params'].diagnosis_id = diagnosis_id

        query = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == helped_status,
                   entities.MedicalBook.diagnosis_id == diagnosis_id)
            .group_by(entities.ItemReview.item_id)
        )

        expected_item_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByDiagnosisSymptoms(_TestOrderMixin,
                                   _TestPaginationMixin,
                                   _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, symptom_ids=[3, 4], match_all_symptoms=True)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, symptom_ids=[3, 4], match_all_symptoms=False)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, symptom_ids=[3, 4], match_all_symptoms=True)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 diagnosis_id=1, symptom_ids=[3, 4], match_all_symptoms=False)
             ),
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_diagnosis_and_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][1]
        symptom_ids = fill_db['symptom_ids'][:2]
        match_all_symptoms = kwargs['filter_params'].match_all_symptoms
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids

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
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestFetchByHelpedStatusDiagnosisSymptoms(_TestOrderMixin,
                                               _TestPaginationMixin,
                                               _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=True,
                 diagnosis_id=1)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=False,
                 diagnosis_id=1)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=True,
                 diagnosis_id=1)
             ),
        dict(include_reviews=False,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=False,
                 diagnosis_id=1)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=True,
                 diagnosis_id=1)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=True, is_helped=False,
                 diagnosis_id=1)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=True,
                 diagnosis_id=1)
             ),
        dict(include_reviews=True,
             filter_params=schemas.FindTreatmentItems(
                 symptom_ids=[3, 4], match_all_symptoms=False, is_helped=False,
                 diagnosis_id=1)
             ),
    ]

    @pytest.mark.parametrize('kwargs', [*TEST_KWARGS])
    def test__fetch_by_helped_status_diagnosis_symptoms(self, kwargs, repo, session,
                                                        fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][2:4]
        helped_status = kwargs['filter_params'].is_helped
        match_all_symptoms = kwargs['filter_params'].match_all_symptoms
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids

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
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_item_ids)
        for item in result:
            assert isinstance(item, entities.TreatmentItem)
            assert item.id in expected_item_ids


class TestUpdateAvgRating:
    def test__update_avg_rating(self, repo, session, fill_db):
        # Setup
        item_id: int = fill_db['item_ids'][0]
        item: entities.TreatmentItem = (
            session.query(entities.TreatmentItem)
            .filter(entities.TreatmentItem.id == item_id)
            .scalar()
        )
        before_avg_rating: float = item.avg_rating

        new_item_review = entities.ItemReview(
            item_id=item_id, is_helped=True, item_rating=10, item_count=1
        )
        session.add(new_item_review)
        session.flush()

        # Call
        repo.update_avg_rating(item)

        # Setup
        after_avg_rating = (
            session.query(func.avg(entities.TreatmentItem.avg_rating))
            .filter(entities.TreatmentItem.id == item_id)
            .scalar()
        )

        # Assert
        assert after_avg_rating != before_avg_rating


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
