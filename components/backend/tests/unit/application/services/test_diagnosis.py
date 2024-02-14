from unittest.mock import Mock

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.DiagnosesRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.Diagnosis:
    return services.Diagnosis(diagnoses_repo=repo)


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [
    entities.Diagnosis(id=1, name='Розацеа', ),
])
def test__get_existing_diagnosis(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.get(diagnosis_id=entity.id)

    # Assert
    repo.get_by_id.assert_called_once_with(entity.id)


@pytest.mark.parametrize("entity", [
    entities.Diagnosis(id=2, name='Атопический дерматит'),
])
def test_get_non_existing_diagnosis(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = None

    # Call and Assert
    with pytest.raises(errors.DiagnosisNotFound):
        service.get(diagnosis_id=entity.id)
    repo.get_by_id.assert_called_once_with(entity.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Diagnosis(name='Розацеа'), dtos.DiagnosisCreateSchema(name='Розацеа'))
])
def test__create_new_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = None
    repo.add.return_value = None

    # Call
    service.create(new_diagnosis_info=dto)

    # Assert
    repo.get_by_name.assert_called_once_with(dto.name)
    repo.add.assert_called_once_with(entity)


@pytest.mark.parametrize("entity, dto", [
    (entities.Diagnosis(id=1, name='Розацеа'), dtos.DiagnosisCreateSchema(name='Розацеа')),
])
def test__create_existing_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_name.return_value = entity

    # Call and Assert
    with pytest.raises(errors.DiagnosisAlreadyExists):
        service.create(new_diagnosis_info=dto)
    repo.get_by_name.assert_called_once_with(dto.name)


@pytest.mark.parametrize("entity, dto", [
    (entities.Diagnosis(id=1, name='Розацеа'), dtos.DiagnosisUpdateSchema(id=1, name='Атопический дерматит')),
])
def test__update_existing_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.update(new_diagnosis_info=dto)

    # Assert
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.DiagnosisUpdateSchema(id=1, name='Псориаз'))
])
def test__update_non_existing_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.DiagnosisNotFound):
        service.update(new_diagnosis_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Diagnosis(id=1, name='Розацеа'), dtos.DiagnosisUpdateSchema(id=1, name='Розацеа')),
])
def test__update_existing_diagnosis_with_same_name(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.DiagnosisAlreadyExists):
        service.update(new_diagnosis_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)


@pytest.mark.parametrize("entity, dto", [
    (entities.Diagnosis(id=1, name='Розацеа'), dtos.DiagnosisDeleteSchema(id=1))
])
def test__delete_existing_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity
    repo.remove.return_value = None

    # Call
    service.delete(diagnosis_info=dto)

    # Assert
    repo.get_by_id.assert_called_once_with(dto.id)
    repo.remove.assert_called_once_with(entity)


@pytest.mark.parametrize("entity, dto", [
    (None, dtos.DiagnosisDeleteSchema(id=1))
])
def test__delete_non_existing_diagnosis(entity, dto, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call and Assert
    with pytest.raises(errors.DiagnosisNotFound):
        service.delete(diagnosis_info=dto)
    repo.get_by_id.assert_called_once_with(dto.id)
