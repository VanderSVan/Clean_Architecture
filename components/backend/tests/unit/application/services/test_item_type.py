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
    return services.ItemType(types_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [entities.ItemType(id=1, name='Крем')])
class TestGet:
    def test__get_existing_type(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.get(type_id=entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(entity.id)]
        assert result == entity

    def test_get_non_existing_type(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.get(type_id=entity.id)

        assert repo.method_calls == [call.fetch_by_id(entity.id)]


class TestCreate:
    @pytest.mark.parametrize("entity, dto, created_entity", [
        (
            entities.ItemType(name='Крем'),
            dtos.ItemTypeCreateSchema(name='Крем'),
            entities.ItemType(id=1, name='Крем')
        )
    ])
    def test__create_new_type(self, entity, dto, created_entity, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = created_entity

        # Call
        result = service.create(new_type_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_name(dto.name), call.add(entity)]
        assert result == created_entity

    @pytest.mark.parametrize("existing_entity, dto", [
        (entities.ItemType(id=1, name='Крем'), dtos.ItemTypeCreateSchema(name='Крем')),
    ])
    def test__create_existing_type(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.ItemTypeAlreadyExists):
            service.create(new_type_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemTypeUpdateSchema(id=1, name='Сыворотка'),
            entities.ItemType(id=1, name='Сыворотка')
        ),
    ])
    def test__change_existing_type(self, existing_entity, dto, updated_entity, service,
                                   repo):
        # Setup
        repo.fetch_by_id.return_value = existing_entity

        # Call
        result = service.change(new_type_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemTypeUpdateSchema(id=1, name='Тоник')
    ])
    def test__change_non_existing_type(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.change(new_type_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemTypeUpdateSchema(id=1, name='Крем')
        ),
    ])
    def test__change_existing_type_with_same_name(self, existing_entity, dto, service,
                                                  repo):
        # Setup
        repo.fetch_by_id.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.ItemTypeAlreadyExists):
            service.change(new_type_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]


class TestDelete:
    @pytest.mark.parametrize("entity, dto", [
        (entities.ItemType(id=1, name='Крем'), dtos.ItemTypeDeleteSchema(id=1))
    ])
    def test__delete_existing_type(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity
        repo.remove.return_value = entity

        # Call
        result = service.delete(item_type_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id), call.remove(entity)]
        assert result == entity

    @pytest.mark.parametrize("dto", [dtos.ItemTypeDeleteSchema(id=1)])
    def test__delete_non_existing_type(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.delete(item_type_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]
