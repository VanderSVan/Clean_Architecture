from unittest.mock import Mock

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
@pytest.mark.parametrize("entity", [
    entities.Symptom(id=1, name='Температура', ),
])
def test__get_existing_symptom(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.get(symptom_id=entity.id)

    # Assert
    repo.get_by_id.assert_called_once_with(entity.id)


@pytest.mark.parametrize("entity", [
    entities.Symptom(id=2, name='Кашель'),
])
def test_get_non_existing_symptom(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = None

    # Call and Assert
    with pytest.raises(errors.SymptomNotFound):
        service.get(symptom_id=entity.id)
    repo.get_by_id.assert_called_once_with(entity.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(name='Температура'), dtos.SymptomCreateSchema(name='Температура'))
])
def test__create_new_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = None
    repo.add.return_value = None

    # Call
    service.create(new_symptom_info=dto)

    # Assert
    repo.get_by_name.assert_called_once_with(dto.name)
    repo.add.assert_called_once_with(entity)


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(id=1, name='Температура'), dtos.SymptomCreateSchema(name='Температура')),
])
def test__create_existing_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = entity

    # Call and Assert
    with pytest.raises(errors.SymptomAlreadyExists):
        service.create(new_symptom_info=dto)
    repo.get_by_name.assert_called_once_with(dto.name)


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(id=1, name='Температура'), dtos.SymptomUpdateSchema(id=1, name='Кашель')),
])
def test__update_existing_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.update(new_symptom_info=dto)

    # Assert
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.SymptomUpdateSchema(id=1, name='Кашель'))
])
def test__update_non_existing_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.SymptomNotFound):
        service.update(new_symptom_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(id=1, name='Температура'), dtos.SymptomUpdateSchema(id=1, name='Температура')),
])
def test__update_existing_symptom_with_same_name(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.SymptomAlreadyExists):
        service.update(new_symptom_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Symptom(id=1, name='Температура'), dtos.SymptomDeleteSchema(id=1))
])
def test__delete_existing_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity
    repo.remove.return_value = None

    # Call
    service.delete(symptom_info=dto)

    # Assert
    repo.get_by_id.assert_called_once_with(dto.id)
    repo.remove.assert_called_once_with(entity)


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.SymptomDeleteSchema(id=1))
])
def test__delete_non_existing_symptom(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.SymptomNotFound):
        service.delete(symptom_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)
