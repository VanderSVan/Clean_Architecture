from itertools import product

import pytest
from sqlalchemy import select, func

from med_sharing_system.adapters.database import tables, repositories
from med_sharing_system.application import entities, dtos, schemas
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
def kwargs_factory(request, fill_db) -> dict[str, bool | schemas.FindMedicalBooks]:
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
        'patient_id': fill_db['patient_ids'][0],
        'item_ids': fill_db['item_ids'],
    }

    for param, value in filter_params:
        if value is None:
            continue
        setattr(filter_params, param, params_to_change.get(param, value))

    request.param['filter_params'] = filter_params

    return request.param


def _combine_data(main: list[dict],
                  mixin: list[dict]
                  ) -> list[dict[str, bool | schemas.FindMedicalBooks]]:
    """
    Комбинирует данные main и mixin, создавая новые экземпляры.
    """
    combined_data: list[dict[str, bool | schemas.FindMedicalBooks]] = []
    for main_data, mixin_data in product(main, mixin):

        if 'filter_params' not in main_data or 'filter_params' not in mixin_data:
            raise KeyError(f"`filter_params` not found in `{main_data=}`. "
                           f"Check your test and parametrize data.")

        main_filter_params_class = main_data['filter_params'].__class__
        if not (isinstance(main_data['filter_params'], schemas.FindMedicalBooks)):
            raise TypeError(f"Expected `filter_params` to be an instance of "
                            f"`{schemas.FindMedicalBooks.__name__}`, "
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
            'include_symptoms': main_data['include_symptoms'],
            'include_reviews': main_data['include_reviews'],
            'filter_params': new_main_filter_params
        })

    return combined_data


def pytest_generate_tests(metafunc):
    """
    Динамически генерирует параметры для тестов,
        только для тех которые имеют суффикс `Mixin`.

    Выполняется до запуска тестов.
    """
    mixin_classes: tuple = (_TestOrderMixin,
                            _TestPaginationMixin,
                            _TestUniquenessMixin)

    for mixin_class in mixin_classes:
        func_name: str = metafunc.function.__name__
        if (
            hasattr(metafunc.cls, 'TEST_KWARGS') and
            hasattr(metafunc.cls, 'OUTPUT_OBJ') and
            len(metafunc.cls.TEST_KWARGS) != len(metafunc.cls.OUTPUT_OBJ)
        ):
            raise AssertionError(
                "Length of `TEST_KWARGS` and `OUTPUT_OBJ` must be equal. "
                f"Check your class `{metafunc.cls}`"
            )

        if hasattr(mixin_class, func_name):
            method_kwargs: list[dict] = metafunc.cls.TEST_KWARGS
            mixin_kwargs: list[dict] = metafunc.cls.MIXIN_KWARGS[func_name]
            combined_kwargs: list[dict] = _combine_data(main=method_kwargs,
                                                        mixin=mixin_kwargs)
            metafunc.parametrize('kwargs_factory', combined_kwargs, indirect=True)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class _BaseMixin:
    TEST_METHOD: str
    TEST_KWARGS: list[dict]
    MIXIN_KWARGS: dict[str, list[dict]] = dict(
        test__order_is_asc=[
            dict(filter_params=schemas.FindMedicalBooks(sort_field='patient_id',
                                                        sort_direction='asc')),
            dict(filter_params=schemas.FindMedicalBooks(sort_field='diagnosis_id',
                                                        sort_direction='asc')),
            dict(filter_params=schemas.FindMedicalBooks(sort_field='title_history',
                                                        sort_direction='asc'))
        ],
        test__order_is_desc=[
            dict(filter_params=schemas.FindMedicalBooks(sort_field='patient_id',
                                                        sort_direction='desc')),
            dict(filter_params=schemas.FindMedicalBooks(sort_field='diagnosis_id',
                                                        sort_direction='desc')),
            dict(filter_params=schemas.FindMedicalBooks(sort_field='title_history',
                                                        sort_direction='desc'))
        ],
        test__with_limit=[dict(filter_params=schemas.FindMedicalBooks(limit=1))],
        test__with_offset=[dict(filter_params=schemas.FindMedicalBooks(offset=1))],
        test__unique_check=[dict(filter_params=schemas.FindMedicalBooks())],
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


class TestFetchById:

    @pytest.mark.parametrize('include_symptoms, include_reviews', [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ])
    def test__fetch_by_id(self, include_symptoms, include_reviews, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id(med_book_id=med_book.id,
                                  include_symptoms=include_symptoms,
                                  include_reviews=include_reviews)

        # Assert
        assert isinstance(result, entities.MedicalBook)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id(med_book_id=10000000,
                                  include_symptoms=False,
                                  include_reviews=False)

        # Assert
        assert result is None


class TestFetchAll(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_all'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks()),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks()),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks()),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks())]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_all(self, kwargs, repo, session):
        # Call
        result = repo.fetch_all(**kwargs)

        # Assert
        assert len(result) > 0
        assert all(isinstance(med_book, entities.MedicalBook) for med_book in result)


class TestFetchBySymptoms(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(symptom_ids=[3, 4])),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(symptom_ids=[3, 4])),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(symptom_ids=[3, 4])),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(symptom_ids=[3, 4]))]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][2:]
        kwargs['filter_params'].symptom_ids = symptom_ids

        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, entities.MedicalBook)
            assert fetched_med_book.id in expected_med_book_ids

            # check symptoms
            if kwargs['include_symptoms']:
                fetched_med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in fetched_med_book.symptoms
                ]
                assert any(symptom_id in fetched_med_book_symptom_ids
                           for symptom_id in kwargs['filter_params'].symptom_ids)


class TestFetchByMatchingAllSymptoms(_TestOrderMixin,
                                     _TestPaginationMixin,
                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], match_all_symptoms=True
                        )),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], match_all_symptoms=True
                        )),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], match_all_symptoms=True
                        )),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], match_all_symptoms=True
                        ))]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_matching_all_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].symptom_ids = symptom_ids

        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, entities.MedicalBook)
            assert fetched_med_book.id in expected_med_book_ids

            # check symptoms
            if kwargs['include_symptoms']:
                assert len(fetched_med_book.symptoms) >= len(symptom_ids)
                fetched_med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in fetched_med_book.symptoms
                ]
                assert all(symptom_id in fetched_med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByDiagnosis(_TestOrderMixin,
                           _TestPaginationMixin,
                           _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(diagnosis_id=1)),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(diagnosis_id=1)),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(diagnosis_id=1)),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(diagnosis_id=1))]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_diagnosis(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == diagnosis_id)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id


class TestFetchByDiagnosisAndSymptoms(_TestOrderMixin,
                                      _TestPaginationMixin,
                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_and_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_diagnosis_and_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [symptom.id
                                                   for symptom in med_book.symptoms]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                  _TestPaginationMixin,
                                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_diagnosis_with_matching_all_symptoms(self, kwargs, repo, session,
                                                            fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        subquery = (
            select(entities.MedicalBook.id.label('med_book_id'),
                   func.count(entities.Symptom.id.distinct()).label('symptom_count'))
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == diagnosis_id,
                   entities.Symptom.id.in_(symptom_ids))
            .group_by(entities.MedicalBook.id)
            .subquery()
        )
        query = (
            select(subquery.c.med_book_id)
            .where(subquery.c.symptom_count == len(symptom_ids))
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_diagnosis_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check symptoms
            if kwargs['include_symptoms']:
                assert len(med_book.symptoms) >= len(symptom_ids)
                med_book_symptom_ids: list[int] = [symptom.id
                                                   for symptom in med_book.symptoms]
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatus(_TestOrderMixin,
                              _TestPaginationMixin,
                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=True)),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False)),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=True)),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False)),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=True)),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False)),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=True)),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False))
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        filter_params: schemas.FindMedicalBooks = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]


class TestFetchByHelpedStatusAndSymptoms(_TestOrderMixin,
                                         _TestPaginationMixin,
                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_and_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2, 3, 4])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2, 3, 4])
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_and_symptoms(self, kwargs, repo, session,
                                                  fill_db):
        # Setup
        symptom_ids = fill_db['symptom_ids']
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params: schemas.FindMedicalBooks = kwargs['filter_params']
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
        result = repo.fetch_by_helped_status_and_symptoms(**kwargs)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatusWithMatchingAllSymptoms(_TestOrderMixin,
                                                     _TestPaginationMixin,
                                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_with_matching_all_symptoms(self, kwargs,
                                                                repo, session, fill_db):
        # Setup
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_helped_status_with_matching_all_symptoms(**kwargs)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatusAndDiagnosis(_TestOrderMixin,
                                          _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_and_diagnosis'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_and_diagnosis(self, kwargs, repo, session, fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_helped_status_and_diagnosis(**kwargs)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]


class TestFetchByHelpedStatusDiagnosisAndSymptoms(_TestOrderMixin,
                                                  _TestPaginationMixin,
                                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_and_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2])
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_diagnosis_and_symptoms(self, kwargs, repo, session,
                                                            fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_helped_status_diagnosis_and_symptoms(**kwargs)

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatusDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                              _TestPaginationMixin,
                                                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
            **kwargs
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == filter_params.diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatient(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(patient_id=1)),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(patient_id=1)),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(patient_id=1)),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(patient_id=1))]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient(self, kwargs, repo, session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        kwargs['filter_params'].patient_id = patient_id

        # Call
        result = repo.fetch_by_patient(**kwargs)

        # Assert
        assert result is not None
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, entities.MedicalBook)
            assert fetched_med_book.patient_id == patient_id


class TestFetchByPatientAndSymptoms(_TestOrderMixin,
                                    _TestPaginationMixin,
                                    _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_and_symptoms(self, kwargs, repo, session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.patient_id == patient_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientWithMatchingAllSymptoms(_TestOrderMixin,
                                                _TestPaginationMixin,
                                                _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_matching_all_symptoms(self, kwargs, repo, session,
                                                     fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.patient_id == patient_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientAndHelpedStatus(_TestOrderMixin,
                                        _TestPaginationMixin,
                                        _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_helped_status'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_and_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_helped_status(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]


class TestFetchByPatientHelpedStatusAndSymptoms(_TestOrderMixin,
                                                _TestPaginationMixin,
                                                _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2])
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_and_symptoms(self, kwargs, repo, session,
                                                          fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientHelpedStatusWithMatchingAllSymptoms(_TestOrderMixin,
                                                            _TestPaginationMixin,
                                                            _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2],
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientHelpedStatusAndDiagnosis(_TestOrderMixin,
                                                 _TestPaginationMixin,
                                                 _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_diagnosis'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, diagnosis_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_and_diagnosis(self, kwargs, repo, session,
                                                           fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_and_diagnosis(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]


class TestFetchByPatientHelpedStatusDiagnosisAndSymptoms(_TestOrderMixin,
                                                         _TestPaginationMixin,
                                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_and_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_diagnosis_and_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_diagnosis_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientHelpedStatusDiagnosisWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, symptom_ids=[1, 2], diagnosis_id=1,
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']

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
            **kwargs
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientDiagnosisWithMatchingAllSymptoms(_TestOrderMixin,
                                                         _TestPaginationMixin,
                                                         _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_diagnosis_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_diagnosis_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientDiagnosisAndSymptoms(_TestOrderMixin,
                                             _TestPaginationMixin,
                                             _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_and_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, symptom_ids=[1, 2], diagnosis_id=1)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_diagnosis_and_symptoms(self, kwargs, repo,
                                                      session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_diagnosis_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientAndDiagnosis(_TestOrderMixin,
                                     _TestPaginationMixin,
                                     _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_diagnosis'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1)
                        )]
    OUTPUT_OBJ = [dtos.MedicalBook, dtos.MedicalBookWithSymptoms,
                  dtos.MedicalBookWithItemReviews,
                  dtos.MedicalBookWithSymptomsAndItemReviews]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_and_diagnosis(self, kwargs, repo, session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_diagnosis(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id


class TestFetchByItems(_TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(item_ids=[1, 2])),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(item_ids=[1, 2])),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(item_ids=[1, 2])),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(item_ids=[1, 2]))]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_items(self, kwargs, repo, session, fill_db):
        # Setup
        item_ids = fill_db['item_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByPatientAndItems(_TestOrderMixin,
                                 _TestPaginationMixin,
                                 _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_and_items'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, item_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_and_items(self, kwargs, repo, session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].patient_id = patient_id
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_patient_and_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByItemsAndHelpedStatus(_TestOrderMixin,
                                      _TestPaginationMixin,
                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_helped_status'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2])),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(is_helped=False, item_ids=[1, 2]))
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_items_and_helped_status(self, kwargs, repo, session, fill_db):
        # Setup
        item_ids = fill_db['item_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_and_helped_status(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByItemsAndDiagnosis(_TestOrderMixin,
                                   _TestPaginationMixin,
                                   _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_diagnosis'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            diagnosis_id=1, item_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_items_and_diagnosis(self, kwargs, repo, session, fill_db):
        # Setup
        item_ids = fill_db['item_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
        query = (
            select(entities.MedicalBook.id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
            .group_by(entities.MedicalBook.id)
        )
        expected_med_book_ids: list[int] = session.execute(query).scalars().all()

        # Call
        result = repo.fetch_by_items_and_diagnosis(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByItemsAndSymptoms(_TestOrderMixin,
                                  _TestPaginationMixin,
                                  _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_and_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_items_and_symptoms(self, kwargs, repo, session,
                                          fill_db):
        # Setup
        symptom_ids = fill_db['symptom_ids'][:2]
        item_ids = fill_db['item_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_items_and_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert any(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                              _TestPaginationMixin,
                                              _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_items_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_items_with_matching_all_symptoms(self, kwargs, repo, session,
                                                        fill_db):
        # Setup
        symptom_ids = fill_db['symptom_ids'][:2]
        item_ids = fill_db['item_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_items_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByDiagnosisItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                                       _TestPaginationMixin,
                                                       _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_diagnosis_items_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            symptom_ids=[1, 2], item_ids=[1, 2], match_all_symptoms=True,
                            diagnosis_id=1)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_diagnosis_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        item_ids = fill_db['item_ids']
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_diagnosis_items_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatusItemsWithMatchingAllSymptoms(_TestOrderMixin,
                                                          _TestPaginationMixin,
                                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_items_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, symptom_ids=[1, 2], item_ids=[1, 2],
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        item_ids = fill_db['item_ids']
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_helped_status_items_with_matching_all_symptoms(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByHelpedStatusDiagnosisAndItems(_TestOrderMixin,
                                               _TestPaginationMixin,
                                               _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_and_items'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2])
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_diagnosis_and_items(self, kwargs, repo, session,
                                                         fill_db):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        item_ids = fill_db['item_ids']
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_helped_status_diagnosis_and_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByHelpedStatusDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = 'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, diagnosis_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        diagnosis_id = fill_db['diagnosis_ids'][0]
        item_ids = fill_db['item_ids']
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
            .fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(**kwargs)
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientDiagnosisAndItems(_TestOrderMixin,
                                          _TestPaginationMixin,
                                          _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_diagnosis_and_items'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2])
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2])
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_diagnosis_and_items(self, kwargs, repo,
                                                   session, fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_diagnosis_and_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByPatientDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = 'fetch_by_patient_diagnosis_items_with_matching_all_symptoms'
    TEST_KWARGS = [dict(include_symptoms=False, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2],
                            symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=False,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2],
                            symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=False, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2],
                            symptom_ids=[1, 2], match_all_symptoms=True)
                        ),
                   dict(include_symptoms=True, include_reviews=True,
                        filter_params=schemas.FindMedicalBooks(
                            patient_id=1, diagnosis_id=1, item_ids=[1, 2],
                            symptom_ids=[1, 2], match_all_symptoms=True)
                        )]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids']
        diagnosis_id = fill_db['diagnosis_ids'][0]
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
            repo.fetch_by_patient_diagnosis_items_with_matching_all_symptoms(**kwargs)
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)

            # check items
            if kwargs['include_reviews']:
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByPatientHelpedStatusAndItems(_TestOrderMixin,
                                             _TestPaginationMixin,
                                             _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_and_items'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2])
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2])
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_and_items(self, kwargs, repo, session,
                                                       fill_db):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids']
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_and_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByPatientHelpedStatusDiagnosisAndItems(_TestOrderMixin,
                                                      _TestPaginationMixin,
                                                      _TestUniquenessMixin):
    TEST_METHOD = 'fetch_by_patient_helped_status_diagnosis_and_items'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], diagnosis_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_diagnosis_and_items(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids']
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
        result = repo.fetch_by_patient_helped_status_diagnosis_and_items(**kwargs)

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)


class TestFetchByPatientHelpedStatusItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = 'fetch_by_patient_helped_status_items_with_matching_all_symptoms'
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids']
        symptom_ids = fill_db['symptom_ids'][:2]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        filter_params = kwargs['filter_params']
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
            .fetch_by_patient_helped_status_items_with_matching_all_symptoms(**kwargs)
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == filter_params.patient_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


class TestFetchByPatientHelpedStatusDiagnosisItemsWithMatchingAllSymptoms(
    _TestOrderMixin, _TestPaginationMixin, _TestUniquenessMixin
):
    TEST_METHOD = (
        'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'
    )
    TEST_KWARGS = [
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=False,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=False, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=True, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             ),
        dict(include_symptoms=True, include_reviews=True,
             filter_params=schemas.FindMedicalBooks(
                 is_helped=False, patient_id=1, item_ids=[1, 2], symptom_ids=[1, 2],
                 match_all_symptoms=True, diagnosis_id=1)
             )
    ]

    @pytest.mark.parametrize('kwargs', TEST_KWARGS)
    def test__fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
        self, kwargs, repo, session, fill_db
    ):
        # Setup
        patient_id = fill_db['patient_ids'][0]
        item_ids = fill_db['item_ids']
        symptom_ids = fill_db['symptom_ids'][:2]
        diagnosis_id = fill_db['diagnosis_ids'][0]
        kwargs['filter_params'].patient_id = patient_id
        kwargs['filter_params'].item_ids = item_ids
        kwargs['filter_params'].symptom_ids = symptom_ids
        kwargs['filter_params'].diagnosis_id = diagnosis_id
        filter_params = kwargs['filter_params']
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
                **kwargs
            )
        )

        # Assert
        assert len(result) > 0
        assert len(result) == len(expected_med_book_ids)
        for med_book in result:
            assert isinstance(med_book, entities.MedicalBook)
            assert med_book.id in expected_med_book_ids
            assert med_book.patient_id == patient_id
            assert med_book.diagnosis_id == diagnosis_id

            # check helped status and items
            if kwargs['include_reviews']:
                assert filter_params.is_helped in [review.is_helped
                                                   for review in med_book.item_reviews]
                assert any(review.item_id in item_ids for review in med_book.item_reviews)

            # check symptoms
            if kwargs['include_symptoms']:
                med_book_symptom_ids: list[int] = [
                    symptom.id for symptom in med_book.symptoms
                ]
                assert len(med_book_symptom_ids) >= len(filter_params.symptom_ids)
                assert all(symptom_id in med_book_symptom_ids
                           for symptom_id in symptom_ids)


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
