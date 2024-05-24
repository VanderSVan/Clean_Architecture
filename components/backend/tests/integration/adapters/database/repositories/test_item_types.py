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
    type_ids: list[int] = test_data.insert_types(session)
    return {'type_ids': type_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.ItemTypesRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:

    def test__fetch_by_id(self, repo, session):
        # Setup
        item_type = session.query(entities.ItemType).first()

        # Call
        result = repo.fetch_by_id(item_type.id)

        # Assert
        assert isinstance(result, entities.ItemType)
        assert result.id == item_type.id


class TestFetchByName:

    def test__fetch_by_name(self, repo, session):
        # Setup
        item_type = session.query(entities.ItemType).first()

        # Call
        result = repo.fetch_by_name(item_type.name)

        # Assert
        assert isinstance(result, entities.ItemType)
        assert result.name == item_type.name


class TestAdd:

    def test__add(self, repo, session):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemType.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.ItemType(name='SomeNewTypeName'))

        # Setup
        after_count = session.execute(
            select(func.count(entities.ItemType.id.distinct()))
        ).scalar()

        # Assert
        assert after_count == before_count + 1
        assert isinstance(result, entities.ItemType)


class TestRemove:

    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemType.id.distinct()))
        ).scalar()
        item_type_to_remove: entities.ItemType = (
            session.query(entities.ItemType).first()
        )

        # Call
        result = repo.remove(item_type_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.ItemType.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.ItemType)
        