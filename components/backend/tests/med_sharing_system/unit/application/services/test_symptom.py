from unittest.mock import Mock, call

import pytest

from med_sharing_system.application import (dtos, entities, errors,
                                            interfaces, services, schemas)


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.SymptomsRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.Symptom:
    return services.Symptom(symptoms_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("entity", [entities.Symptom(id=1, name='Температура')])
class TestGet:

    def test__get_symptom(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.get(symptom_id=entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(entity.id)]
        assert result == dtos.Symptom.from_orm(entity)

    def test_get_non_existing_symptom(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.get(symptom_id=entity.id)

        assert repo.method_calls == [call.fetch_by_id(entity.id)]


class TestFindSymptoms:
    @pytest.mark.parametrize("result_output", [
        [
            entities.Symptom(id=1, name='Температура'),
            entities.Symptom(id=2, name='Давление'),
        ],
    ])
    def test__with_keywords(self, result_output, service, repo):
        # Setup
        repo.search_by_name.return_value = result_output
        filter_params = schemas.FindSymptoms(keywords='Темп')

        # Call
        result = service.find_symptoms(filter_params=filter_params)

        # Assert
        assert repo.method_calls == [call.search_by_name(filter_params)]
        assert result == [dtos.Symptom.from_orm(entity) for entity in result_output]

    @pytest.mark.parametrize("result_output", [
        [
            entities.Symptom(id=1, name='Температура'),
            entities.Symptom(id=2, name='Давление'),
        ]
    ])
    def test__without_keywords(self, result_output, service, repo):
        # Setup
        repo.fetch_all.return_value = result_output
        filter_params = schemas.FindSymptoms()

        # Call
        result = service.find_symptoms(filter_params=filter_params)

        # Assert
        assert repo.method_calls == [call.fetch_all(filter_params)]
        assert result == [dtos.Symptom.from_orm(entity) for entity in result_output]


class TestCreate:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.Symptom(name='Температура'),
            dtos.NewSymptomInfo(name='Температура'),
            entities.Symptom(id=1, name='Температура')
        )
    ])
    def test__create_new_symptom(self, new_entity, dto, created_entity, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = created_entity

        # Call
        result = service.add(new_symptom_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_name(dto.name), call.add(new_entity)]
        assert result == dtos.Symptom.from_orm(created_entity)

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.Symptom(id=1, name='Температура'),
            dtos.NewSymptomInfo(name='Температура')
        )
    ])
    def test__create_existing_symptom(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.SymptomAlreadyExists):
            service.add(new_symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("repo_output, dto, service_output", [
        (
            entities.Symptom(id=1, name='Температура'),
            dtos.Symptom(id=1, name='Кашель'),
            entities.Symptom(id=1, name='Кашель')
        ),
    ])
    def test__change(self, repo_output, dto, service_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output
        repo.fetch_by_name.return_value = None

        # Call
        result = service.change(new_symptom_info=dto)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_id(dto.id),
            call.fetch_by_name(dto.name)
        ]
        assert result == dtos.Symptom.from_orm(service_output)

    @pytest.mark.parametrize("dto", [
        dtos.Symptom(id=1, name='Кашель')
    ])
    def test__change_non_existing_symptom(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.change(new_symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (entities.Symptom(id=1, name='Температура'),
         dtos.Symptom(id=2, name='Температура')),
    ])
    def test__change_existing_symptom_with_same_name(self, existing_entity, dto, service,
                                                     repo):
        # Setup
        repo.fetch_by_id.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.SymptomAlreadyExists):
            service.change(new_symptom_info=dto)

        assert repo.method_calls == [
            call.fetch_by_id(dto.id),
            call.fetch_by_name(dto.name)
        ]


class TestDelete:
    @pytest.mark.parametrize("existing_entity", [
        entities.Symptom(id=1, name='Температура')
    ])
    def test__delete_existing_symptom(self, existing_entity, service, repo):
        # Setup
        symptom_id = 1
        repo.fetch_by_id.return_value = existing_entity
        repo.remove.return_value = existing_entity

        # Call
        result = service.delete(symptom_id=symptom_id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(symptom_id),
                                     call.remove(existing_entity)]
        assert result == dtos.Symptom.from_orm(existing_entity)

    def test__delete_non_existing_symptom(self, service, repo):
        # Setup
        symptom_id = 1
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.delete(symptom_id=symptom_id)

        assert repo.method_calls == [call.fetch_by_id(symptom_id)]
