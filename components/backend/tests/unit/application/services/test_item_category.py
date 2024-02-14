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
    return services.ItemCategory(item_categories_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [
    entities.ItemCategory(id=1, name='Аптечные продукты'),
])
def test__get_existing_item_category(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.get(item_category_id=entity.id)

    # Assert
    expected_calls_for_repo = [call.get_by_id(entity.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity", [
    entities.ItemCategory(id=2, name='Уходовая косметика'),
])
def test_get_non_existing_item_category(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = None

    # Call and Assert
    with pytest.raises(errors.ItemCategoryNotFound):
        service.get(item_category_id=entity.id)

    expected_calls_for_repo = [call.get_by_id(entity.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemCategory(name='Аптечные продукты'), dtos.ItemCategoryCreateSchema(name='Аптечные продукты'))
])
def test__create_new_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = None
    repo.add.return_value = None

    # Call
    service.create(new_item_category_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_name(dto.name), call.add(entity)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemCategory(id=1, name='Аптечные продукты'), dtos.ItemCategoryCreateSchema(name='Аптечные продукты')),
])
def test__create_existing_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemCategoryAlreadyExists):
        service.create(new_item_category_info=dto)

    expected_calls_for_repo = [call.get_by_name(dto.name)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategoryUpdateSchema(id=1, name='Уходовая косметика')
    ),
])
def test__update_existing_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.update(new_item_category_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.ItemCategoryUpdateSchema(id=1, name='Псориаз'))
])
def test__update_non_existing_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemCategoryNotFound):
        service.update(new_item_category_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategoryUpdateSchema(id=1, name='Аптечные продукты')
    ),
])
def test__update_existing_item_category_with_same_name(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemCategoryAlreadyExists):
        service.update(new_item_category_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemCategory(id=1, name='Аптечные продукты'), dtos.ItemCategoryDeleteSchema(id=1))
])
def test__delete_existing_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity
    repo.remove.return_value = None

    # Call
    service.delete(item_category_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_id(dto.id), call.remove(entity)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.ItemCategoryDeleteSchema(id=1))
])
def test__delete_non_existing_item_category(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemCategoryNotFound):
        service.delete(item_category_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo
