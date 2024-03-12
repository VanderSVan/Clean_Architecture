import pytest

from sqlalchemy import exc

from simple_medication_selection.adapters.database import tables, repositories
from simple_medication_selection.application import entities
from .. import test_data


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    symptom_ids: list[int] = test_data.insert_symptoms(session)
    return {'symptom_ids': symptom_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.SymptomsRepo(context=transaction_context)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
class TestFetchAll:
    def test__fetch_all(self, repo):
        result = repo.fetch_all(limit=None, offset=None)

        assert len(result) == len(test_data.SYMPTOMS_DATA)
        for symptom in result:
            assert isinstance(symptom, entities.Symptom)

    def test__with_limit(self, repo):
        result = repo.fetch_all(limit=1, offset=None)

        assert len(result) == 1

    def test__with_offset(self, repo):
        result = repo.fetch_all(limit=None, offset=1)

        assert len(result) == len(test_data.SYMPTOMS_DATA) - 1


class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        symptom = session.query(entities.Symptom).first()

        fetched_symptom = repo.fetch_by_id(symptom.id)

        assert isinstance(fetched_symptom, entities.Symptom)


class TestFetchByName:
    def test__fetch_by_name(self, repo, fill_db):
        result = repo.fetch_by_name(test_data.SYMPTOMS_DATA[0]['name'])

        assert result.name == test_data.SYMPTOMS_DATA[0]['name']
        assert isinstance(result, entities.Symptom)


class TestAdd:
    def test__add(self, repo, session):
        before_count = len(session.execute(tables.symptoms.select()).all())

        result = repo.add(entities.Symptom(name='New symptom'))

        after_count = len(session.execute(tables.symptoms.select()).all())

        assert before_count + 1 == after_count
        assert isinstance(result, entities.Symptom)

    def test__already_exists(self, repo):
        with pytest.raises(exc.IntegrityError):
            repo.add(entities.Symptom(name=test_data.SYMPTOMS_DATA[0]['name']))


class TestRemove:
    def test__remove(self, repo, session):
        before_count = len(session.execute(tables.symptoms.select()).all())

        symptom = session.query(entities.Symptom).first()
        result = repo.remove(symptom)

        after_count = len(session.execute(tables.symptoms.select()).all())

        assert before_count - 1 == after_count
        assert isinstance(result, entities.Symptom)
