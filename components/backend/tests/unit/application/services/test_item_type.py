from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.ItemTypesRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.ItemType:
    return services.ItemType(item_types_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [
    entities.ItemType(id=1, name='Крем'),
])
def test__get_existing_item_type(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.get(item_type_id=entity.id)

    # Assert
    expected_calls_for_repo = [call.get_by_id(entity.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity", [
    entities.ItemType(id=2, name='Сыворотка'),
])
def test_get_non_existing_item_type(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = None

    # Call and Assert
    with pytest.raises(errors.ItemTypeNotFound):
        service.get(item_type_id=entity.id)

    expected_calls_for_repo = [call.get_by_id(entity.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemType(name='Крем'), dtos.ItemTypeCreateSchema(name='Крем'))
])
def test__create_new_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = None
    repo.add.return_value = None

    # Call
    service.create(new_item_type_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_name(dto.name), call.add(entity)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemType(id=1, name='Крем'), dtos.ItemTypeCreateSchema(name='Крем')),
])
def test__create_existing_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemTypeAlreadyExists):
        service.create(new_item_type_info=dto)

    expected_calls_for_repo = [call.get_by_name(dto.name)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemTypeUpdateSchema(id=1, name='Сыворотка')
    ),
])
def test__update_existing_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.update(new_item_type_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.ItemTypeUpdateSchema(id=1, name='Тоник'))
])
def test__update_non_existing_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemTypeNotFound):
        service.update(new_item_type_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemType(id=1, name='Крем'), dtos.ItemTypeUpdateSchema(id=1, name='Крем')),
])
def test__update_existing_item_type_with_same_name(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemTypeAlreadyExists):
        service.update(new_item_type_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (entities.ItemType(id=1, name='Крем'), dtos.ItemTypeDeleteSchema(id=1))
])
def test__delete_existing_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity
    repo.remove.return_value = None

    # Call
    service.delete(item_type_info=dto)

    # Assert
    expected_calls_for_repo = [call.get_by_id(dto.id), call.remove(entity)]
    assert repo.method_calls == expected_calls_for_repo


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.ItemTypeDeleteSchema(id=1))
])
def test__delete_non_existing_item_type(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.ItemTypeNotFound):
        service.delete(item_type_info=dto)

    expected_calls_for_repo = [call.get_by_id(dto.id)]
    assert repo.method_calls == expected_calls_for_repo
