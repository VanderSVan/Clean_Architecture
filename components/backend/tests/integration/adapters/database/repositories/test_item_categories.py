import pytest

from sqlalchemy import select, func

from simple_medication_selection.adapters.database import repositories
from simple_medication_selection.application import entities, schemas
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
        

class TestFetchAll:
    def test__fetch_all(self, repo):
        filter_params = schemas.FindItemCategories(sort_field='name',
                                              sort_direction='asc')
        result = repo.fetch_all(filter_params)

        assert len(result) == len(test_data.CATEGORIES_DATA)
        for ItemCategory in result:
            assert isinstance(ItemCategory, entities.ItemCategory)

    def test__with_limit(self, repo):
        filter_params = schemas.FindItemCategories(sort_field='name',
                                              sort_direction='asc',
                                              limit=1)
        result = repo.fetch_all(filter_params)

        assert len(result) == filter_params.limit

    def test__with_offset(self, repo):
        filter_params = schemas.FindItemCategories(sort_field='name',
                                              sort_direction='asc',
                                              offset=1)
        result = repo.fetch_all(filter_params)

        assert len(result) == len(test_data.CATEGORIES_DATA) - filter_params.offset


class TestSearchByName:
    def test__search_by_name(self, repo, fill_db):
        # Setup
        filter_params = schemas.FindItemCategories(
            keywords=test_data.CATEGORIES_DATA[0]['name'][:5],
            sort_field='name',
            sort_direction='asc'
        )

        # Call
        result = repo.search_by_name(filter_params)

        # Assert
        assert len(result) == 3
        assert isinstance(result[0], entities.ItemCategory)

    def test__with_limit(self, repo, fill_db):
        # Setup
        filter_params = schemas.FindItemCategories(
            keywords=test_data.CATEGORIES_DATA[0]['name'][:5],
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
        filter_params = schemas.FindItemCategories(
            keywords=test_data.CATEGORIES_DATA[0]['name'][:5],
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
