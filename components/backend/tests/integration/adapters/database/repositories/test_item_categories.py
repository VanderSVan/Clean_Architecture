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
    category_ids: list[int] = test_data.insert_categories(session)
    return {'category_ids': category_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.ItemCategoriesRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        category = session.query(entities.ItemCategory).first()

        # Call
        result = repo.fetch_by_id(category.id)

        # Assert
        assert isinstance(result, entities.ItemCategory)
        assert result.id == category.id


class TestFetchByName:
    def test__fetch_by_name(self, repo, session):
        # Setup
        category = session.query(entities.ItemCategory).first()

        # Call
        result = repo.fetch_by_name(category.name)

        # Assert
        assert isinstance(result, entities.ItemCategory)
        assert result.name == category.name


class TestAdd:
    def test__add(self, repo, session):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemCategory.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.ItemCategory(name='SomeNewCategoryName'))

        # Setup
        after_count = session.execute(
            select(func.count(entities.ItemCategory.id.distinct()))
        ).scalar()

        # Assert
        assert after_count == before_count + 1
        assert isinstance(result, entities.ItemCategory)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemCategory.id.distinct()))
        ).scalar()
        category_to_remove: entities.ItemCategory = (
            session.query(entities.ItemCategory).first()
        )

        # Call
        result = repo.remove(category_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.ItemCategory.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.ItemCategory)
