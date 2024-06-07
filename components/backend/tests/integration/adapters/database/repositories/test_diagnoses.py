import pytest
from sqlalchemy import select, func

from med_sharing_system.adapters.database import repositories
from med_sharing_system.application import entities, schemas
from .. import test_data


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    diagnosis_ids: list[int] = test_data.insert_diagnoses(session)
    return {'diagnosis_ids': diagnosis_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.DiagnosesRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        diagnosis = session.query(entities.Diagnosis).first()

        # Call
        result = repo.fetch_by_id(diagnosis.id)

        # Assert
        assert isinstance(result, entities.Diagnosis)
        assert result.id == diagnosis.id


class TestFetchByName:
    def test__fetch_by_name(self, repo, session):
        # Setup
        diagnosis = session.query(entities.Diagnosis).first()

        # Call
        result = repo.fetch_by_name(diagnosis.name)

        # Assert
        assert isinstance(result, entities.Diagnosis)
        assert result.name == diagnosis.name


class TestFetchAll:
    def test__fetch_all(self, repo):
        filter_params = schemas.FindDiagnoses(sort_field='name',
                                              sort_direction='asc')
        result = repo.fetch_all(filter_params)

        assert len(result) == len(test_data.DIAGNOSES_DATA)
        for diagnosis in result:
            assert isinstance(diagnosis, entities.Diagnosis)

    def test__with_limit(self, repo):
        filter_params = schemas.FindDiagnoses(sort_field='name',
                                              sort_direction='asc',
                                              limit=1)
        result = repo.fetch_all(filter_params)

        assert len(result) == filter_params.limit

    def test__with_offset(self, repo):
        filter_params = schemas.FindDiagnoses(sort_field='name',
                                              sort_direction='asc',
                                              offset=1)
        result = repo.fetch_all(filter_params)

        assert len(result) == len(test_data.DIAGNOSES_DATA) - filter_params.offset


class TestSearchByName:
    def test__search_by_name(self, repo, fill_db):
        # Setup
        filter_params = schemas.FindDiagnoses(
            keywords=test_data.DIAGNOSES_DATA[0]['name'][:5],
            sort_field='name',
            sort_direction='asc'
        )

        # Call
        result = repo.search_by_name(filter_params)

        # Assert
        assert len(result) == 3
        assert isinstance(result[0], entities.Diagnosis)

    def test__with_limit(self, repo, fill_db):
        # Setup
        filter_params = schemas.FindDiagnoses(
            keywords=test_data.DIAGNOSES_DATA[0]['name'][:5],
            sort_field='name',
            sort_direction='asc',
            limit=1
        )

        # Call
        result = repo.search_by_name(filter_params)

        # Assert
        assert len(result) == 1

    def test__with_offset(self, repo, fill_db):
        # Setup
        filter_params = schemas.FindDiagnoses(
            keywords=test_data.DIAGNOSES_DATA[0]['name'][:5],
            sort_field='name',
            sort_direction='asc',
            offset=1
        )

        # Call
        result = repo.search_by_name(filter_params)

        # Assert
        assert len(result) == 2


class TestAdd:
    def test__add(self, repo, session):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Diagnosis.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.Diagnosis(name='SomeNewDiagnosisName'))

        # Setup
        after_count = session.execute(
            select(func.count(entities.Diagnosis.id.distinct()))
        ).scalar()

        # Assert
        assert after_count == before_count + 1
        assert isinstance(result, entities.Diagnosis)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Diagnosis.id.distinct()))
        ).scalar()
        diagnosis_to_remove: entities.Diagnosis = (
            session.query(entities.Diagnosis).first()
        )

        # Call
        result = repo.remove(diagnosis_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.Diagnosis.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.Diagnosis)
