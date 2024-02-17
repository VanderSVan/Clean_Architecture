from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


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

    def test__get_existing_symptom(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.get(symptom_id=entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(entity.id)]
        assert result == entity

    def test_get_non_existing_symptom(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.get(symptom_id=entity.id)

        assert repo.method_calls == [call.fetch_by_id(entity.id)]


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(name='Температура'), dtos.SymptomCreateSchema(name='Температура'))
])
class TestCreate:

    def test__create_new_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = entity

        # Call
        result = service.create(new_symptom_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_name(dto.name), call.add(entity)]
        assert result == entity

    def test__create_existing_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = entity

        # Call and Assert
        with pytest.raises(errors.SymptomAlreadyExists):
            service.create(new_symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("entity, dto", [
        (
            entities.Symptom(id=1, name='Температура'),
            dtos.SymptomUpdateSchema(id=1, name='Кашель')
        ),
    ])
    def test__change_existing_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.change(new_symptom_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id)]
        assert result == entity

    @pytest.mark.parametrize("entity, dto", [
        (None, dtos.SymptomUpdateSchema(id=1, name='Кашель'))
    ])
    def test__change_non_existing_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.change(new_symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("entity, dto", [
        (entities.Symptom(id=1, name='Температура'),
         dtos.SymptomUpdateSchema(id=2, name='Температура')),
    ])
    def test__change_existing_symptom_with_same_name(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call and Assert
        with pytest.raises(errors.SymptomAlreadyExists):
            service.change(new_symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]


class TestDelete:
    @pytest.mark.parametrize("entity, dto", [
        (entities.Symptom(id=1, name='Температура'), dtos.SymptomDeleteSchema(id=1))
    ])
    def test__delete_existing_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity
        repo.remove.return_value = entity

        # Call
        result = service.delete(symptom_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id), call.remove(entity)]
        assert result == entity

    @pytest.mark.parametrize("entity, dto", [
        (None, dtos.SymptomDeleteSchema(id=1))
    ])
    def test__delete_non_existing_symptom(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.delete(symptom_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]
