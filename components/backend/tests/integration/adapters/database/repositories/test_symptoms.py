import pytest

from sqlalchemy import exc

from simple_medication_selection.adapters.database import (
    tables,
    repositories
)
from simple_medication_selection.application import entities

# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
SYMPTOMS_DATA = [
    {'name': 'Температура'},
    {'name': 'Давление'},
    {'name': 'Покраснение лица'}
]


@pytest.fixture(scope='function', autouse=True)
def fill_db(session):
    session.execute(tables.symptoms.insert(), SYMPTOMS_DATA)


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.SymptomsRepo(context=transaction_context)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
class TestFetchAll:
    def test__fetch_all(self, repo):
        result = repo.fetch_all(limit=None, offset=None)

        assert len(result) == len(SYMPTOMS_DATA)
        assert isinstance(result[0], entities.Symptom)

    def test__fetch_all__with_limit(self, repo):
        result = repo.fetch_all(limit=1, offset=None)

        assert len(result) == 1

    def test__fetch_all__with_offset(self, repo):
        result = repo.fetch_all(limit=None, offset=1)

        assert len(result) == len(SYMPTOMS_DATA) - 1

    def test__fetch_all__empty_result(self, repo):
        result = repo.fetch_all(limit=10, offset=10)

        assert len(result) == 0
        assert result == []


class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        symptom = session.query(entities.Symptom).first()

        fetched_symptom = repo.fetch_by_id(symptom.id)

        assert fetched_symptom is not None
        assert isinstance(fetched_symptom, entities.Symptom)

    def test__fetch_by_id__not_found(self, repo):
        result = repo.fetch_by_id(100)

        assert result is None


class TestFetchByName:
    def test__fetch_by_name(self, repo):
        result = repo.fetch_by_name('Давление')

        assert result.name == 'Давление'
        assert isinstance(result, entities.Symptom)

    def test__fetch_by_name__not_found(self, repo):
        result = repo.fetch_by_name('Test symptom')

        assert result is None


class TestAdd:
    def test__add(self, repo, session):
        before_count = len(session.execute(tables.symptoms.select()).all())

        result = repo.add(entities.Symptom(name='New symptom'))

        after_count = len(session.execute(tables.symptoms.select()).all())

        assert before_count + 1 == after_count
        assert isinstance(result, entities.Symptom)

    def test__add__already_exists(self, repo):
        with pytest.raises(exc.IntegrityError):
            repo.add(entities.Symptom(name='Температура'))


class TestRemove:
    def test__remove(self, repo, session):
        before_count = len(session.execute(tables.symptoms.select()).all())

        symptom = session.query(entities.Symptom).first()
        result = repo.remove(symptom)

        after_count = len(session.execute(tables.symptoms.select()).all())

        assert before_count - 1 == after_count
        assert isinstance(result, entities.Symptom)
