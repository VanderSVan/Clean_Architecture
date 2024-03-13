import pytest

from sqlalchemy import select, func

from simple_medication_selection.adapters.database import repositories
from simple_medication_selection.application import entities
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
