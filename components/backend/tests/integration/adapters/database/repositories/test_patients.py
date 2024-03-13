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
    patient_ids: list[int] = test_data.insert_patients(session)
    return {'patient_ids': patient_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.PatientsRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()

        # Call
        result = repo.fetch_by_id(patient.id)

        # Assert
        assert isinstance(result, entities.Patient)
        assert result.id == patient.id


class TestFetchByNickname:
    def test__fetch_by_nickname(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()

        # Call
        result = repo.fetch_by_nickname(patient.nickname)

        # Assert
        assert isinstance(result, entities.Patient)
        assert result.nickname == patient.nickname


class TestAdd:
    def test__add(self, repo, session):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.Patient(nickname='SomeAmazingNickname',
                                           gender='female',
                                           age=20,
                                           skin_type='сухая'))

        # Setup
        after_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.Patient)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()
        patient_to_remove: entities.Patient = session.query(entities.Patient).first()

        # Call
        result = repo.remove(patient_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.Patient)
