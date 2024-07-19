from unittest.mock import Mock, call

import pytest

from med_sharing_system.application import (
    dtos, entities, errors, interfaces, services, schemas
)


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

class TestGet:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemType(id=1, name='Крем')
        )
    ])
    def test__get_type(self, repo_output, service_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get(type_id=repo_output.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(repo_output.id)]
        assert result == service_output

    @pytest.mark.parametrize("repo_output", [entities.ItemType(id=1, name='Крем')])
    def test_get_non_existing_type(self, repo_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.get(type_id=repo_output.id)

        assert repo.method_calls == [call.fetch_by_id(repo_output.id)]


class TestFind:
    @pytest.mark.parametrize("repo_output, filter_params, service_output", [
        (
            [entities.ItemType(id=1, name='Крема')],
            schemas.FindItemTypes(keywords='кре'),
            [dtos.ItemType(id=1, name='Крема')]
        )
    ])
    def test__find_by_keywords(self, repo_output, filter_params, service_output, service,
                               repo):
        # Setup
        repo.search_by_name.return_value = repo_output

        # Call
        result = service.find(filter_params=filter_params)

        # Assert
        assert repo.method_calls == [call.search_by_name(filter_params)]
        assert result == service_output

    @pytest.mark.parametrize("repo_output, filter_params, service_output", [
        (
            [entities.ItemType(id=1, name='Крема')],
            schemas.FindItemTypes(),
            [dtos.ItemType(id=1, name='Крема')]
        )
    ])
    def test__find_without_keywords(self, repo_output, filter_params, service_output,
                                    service, repo):
        # Setup
        repo.fetch_all.return_value = repo_output

        # Call
        result = service.find(filter_params=filter_params)

        # Assert
        assert repo.method_calls == [call.fetch_all(filter_params)]
        assert result == service_output


class TestAdd:
    @pytest.mark.parametrize("new_entity, input_dto, repo_output, service_output", [
        (
            entities.ItemType(name='Крем'),
            dtos.NewItemTypeInfo(name='Крем'),
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemType(id=1, name='Крем')
        )
    ])
    def test__add_new_type(self, new_entity, input_dto, repo_output, service_output,
                           service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = repo_output

        # Call
        result = service.add(new_type_info=input_dto)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_name(input_dto.name),
            call.add(new_entity)
        ]
        assert result == service_output

    @pytest.mark.parametrize("existing_entity, dto", [
        (entities.ItemType(id=1, name='Крем'), dtos.NewItemTypeInfo(name='Крем')),
    ])
    def test__type_already_exists(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.ItemTypeAlreadyExists):
            service.add(new_type_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("repo_output, new_info, service_output", [
        (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemType(id=1, name='Сыворотка'),
            dtos.ItemType(id=1, name='Сыворотка')
        ),
    ])
    def test__change_type(self, repo_output, new_info, service_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output
        repo.fetch_by_name.return_value = None

        # Call
        result = service.change(new_type_info=new_info)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_id(new_info.id),
            call.fetch_by_name(new_info.name)
        ]
        assert result == service_output

    @pytest.mark.parametrize("dto", [
        dtos.ItemType(id=1, name='Тоник')
    ])
    def test__type_not_found(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.change(new_type_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("repo_fetch_by_id_output, repo_fetch_by_name_output, dto", [
        (
            entities.ItemType(id=1, name='Крем'),
            dtos.ItemType(id=2, name='Крем'),
            dtos.ItemType(id=1, name='Крем')
        ),
    ])
    def test__change_existing_type_with_same_name(
        self, repo_fetch_by_id_output, repo_fetch_by_name_output, dto, service, repo
    ):
        # Setup
        repo.fetch_by_id.return_value = repo_fetch_by_id_output
        repo.fetch_by_name.return_value = repo_fetch_by_name_output

        # Call and Assert
        with pytest.raises(errors.ItemTypeAlreadyExists):
            service.change(new_type_info=dto)

        assert repo.method_calls == [
            call.fetch_by_id(dto.id),
            call.fetch_by_name(dto.name)
        ]


class TestDelete:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.ItemCategory(id=1, name='Крем'),
            dtos.ItemCategory(id=1, name='Крем')
        )
    ])
    def test__delete_type(self, repo_output, service_output, service, repo):
        # Setup
        type_id = 1
        repo.fetch_by_id.return_value = repo_output
        repo.remove.return_value = repo_output

        # Call
        result = service.delete(type_id=type_id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(type_id),
                                     call.remove(repo_output)]
        assert result == service_output

    def test__delete_non_existing_type(self, service, repo):
        # Setup
        type_id = 1
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.delete(type_id=type_id)

        assert repo.method_calls == [call.fetch_by_id(type_id)]
