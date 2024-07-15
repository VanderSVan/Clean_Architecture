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
    return Mock(interfaces.ItemCategoriesRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.ItemCategory:
    return services.ItemCategory(categories_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------

class TestGet:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategory(id=1, name='Аптечные продукты')
        )
    ])
    def test__get(self, repo_output, service_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get(category_id=repo_output.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(repo_output.id)]
        assert result == service_output

    @pytest.mark.parametrize("repo_output", [
        entities.ItemCategory(id=1, name='Аптечные продукты')
    ])
    def test_get_non_existing_category(self, repo_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.get(category_id=repo_output.id)

        assert repo.method_calls == [call.fetch_by_id(repo_output.id)]


class TestFind:
    @pytest.mark.parametrize("repo_output, filter_params, service_output", [
        (
            [entities.ItemCategory(id=1, name='Аптечные продукты')],
            schemas.FindItemCategories(keywords='аптеч'),
            [dtos.ItemCategory(id=1, name='Аптечные продукты')]
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
            [entities.ItemCategory(id=1, name='Аптечные продукты')],
            schemas.FindItemCategories(),
            [dtos.ItemCategory(id=1, name='Аптечные продукты')]
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
            entities.ItemCategory(name='Аптечные продукты'),
            dtos.NewItemCategoryInfo(name='Аптечные продукты'),
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategory(id=1, name='Аптечные продукты')
        )
    ])
    def test__add_new_category(self, new_entity, input_dto, repo_output, service_output,
                               service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = repo_output

        # Call
        result = service.add(new_category_info=input_dto)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_name(input_dto.name),
            call.add(new_entity)
        ]
        assert result == service_output

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.NewItemCategoryInfo(name='Аптечные продукты')
        ),
    ])
    def test__add_existing_category(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.ItemCategoryAlreadyExists):
            service.add(new_category_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("repo_output, new_info, service_output", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategory(id=1, name='Уходовая косметика'),
            dtos.ItemCategory(id=1, name='Уходовая косметика')
        ),
    ])
    def test__change_category(self, repo_output, new_info, service_output,
                              service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output
        repo.fetch_by_name.return_value = None

        # Call
        result = service.change(new_category_info=new_info)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_id(new_info.id),
            call.fetch_by_name(new_info.name)
        ]
        assert result == service_output

    @pytest.mark.parametrize("dto", [
        dtos.ItemCategory(id=1, name='Псориаз')
    ])
    def test__category_not_found(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.change(new_category_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("repo_fetch_by_id_output, repo_fetch_by_name_output, dto", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategory(id=2, name='Аптечные продукты'),
            dtos.ItemCategory(id=1, name='Аптечные продукты')
        ),
    ])
    def test__change_category_with_same_name(
        self, repo_fetch_by_id_output, repo_fetch_by_name_output, dto, service, repo
    ):
        # Setup
        repo.fetch_by_id.return_value = repo_fetch_by_id_output
        repo.fetch_by_name.return_value = repo_fetch_by_name_output

        # Call and Assert
        with pytest.raises(errors.ItemCategoryAlreadyExists):
            service.change(new_category_info=dto)

        assert repo.method_calls == [
            call.fetch_by_id(dto.id),
            call.fetch_by_name(dto.name)
        ]


class TestDelete:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.ItemCategory(id=1, name='Аптечные продукты'),
            dtos.ItemCategory(id=1, name='Аптечные продукты')
        )
    ])
    def test__delete_category(self, repo_output, service_output, service, repo):
        # Setup
        category_id = 1
        repo.fetch_by_id.return_value = repo_output
        repo.remove.return_value = repo_output

        # Call
        result = service.delete(category_id=category_id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(category_id),
                                     call.remove(repo_output)]
        assert result == service_output

    def test__category_not_found(self, service, repo):
        # Setup
        category_id = 1
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.delete(category_id=category_id)

        assert repo.method_calls == [call.fetch_by_id(category_id)]
