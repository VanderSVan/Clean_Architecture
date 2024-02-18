from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.ItemCategoriesRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.ItemCategory:
    return services.ItemCategory(categories_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [
    entities.ItemCategory(id=1, name='Аптечные продукты'),
])
class TestGet:
    def test__get_existing_item_category(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.get(category_id=entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(entity.id)]
        assert result == entity

    def test_get_non_existing_item_category(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.get(category_id=entity.id)

        assert repo.method_calls == [call.fetch_by_id(entity.id)]


class TestCreate:
    @pytest.mark.parametrize("entity, dto, created_entity", [
        (
            entities.ItemCategory(name='Аптечные продукты'),
            dtos.ItemCategoryCreateSchema(name='Аптечные продукты'),
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
    ])
    def test__create_new_item_category(self, entity, dto, created_entity, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = created_entity

        # Call
        result = service.create(new_category_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_name(dto.name), call.add(entity)]
        assert result == created_entity

    @pytest.mark.parametrize("entity, dto", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategoryCreateSchema(name='Аптечные продукты')
        ),
    ])
    def test__create_existing_item_category(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = entity

        # Call and Assert
        with pytest.raises(errors.ItemCategoryAlreadyExists):
            service.create(new_category_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("entity, dto, updated_entity", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategoryUpdateSchema(id=1, name='Уходовая косметика'),
            entities.ItemCategory(id=1, name='Уходовая косметика')
        ),
    ])
    def test__change_existing_item_category(self, entity, dto, updated_entity, service,
                                            repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.change(new_category_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemCategoryUpdateSchema(id=1, name='Псориаз')
    ])
    def test__change_non_existing_item_category(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.change(new_category_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("entity, dto", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategoryUpdateSchema(id=1, name='Аптечные продукты')
        ),
    ])
    def test__change_existing_item_category_with_same_name(self, entity, dto, service,
                                                           repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call and Assert
        with pytest.raises(errors.ItemCategoryAlreadyExists):
            service.change(new_category_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]


class TestDelete:
    @pytest.mark.parametrize("entity, dto", [
        (entities.ItemCategory(id=1, name='Аптечные продукты'),
         dtos.ItemCategoryDeleteSchema(id=1))
    ])
    def test__delete_existing_item_category(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity
        repo.remove.return_value = entity

        # Call
        result = service.delete(item_category_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id), call.remove(entity)]
        assert result == entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemCategoryDeleteSchema(id=1)
    ])
    def test__delete_non_existing_item_category(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.delete(item_category_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]
