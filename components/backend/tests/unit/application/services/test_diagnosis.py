from unittest.mock import Mock, call

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
class TestGet:

    def test__get_existing_diagnosis(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.get(diagnosis_id=entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(entity.id)]
        assert result == entity

    def test_get_non_existing_diagnosis(self, entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.get(diagnosis_id=entity.id)

        assert repo.method_calls == [call.fetch_by_id(entity.id)]


class TestCreate:
    @pytest.mark.parametrize("entity, dto, returned_entity", [
        (
            entities.Diagnosis(name='Розацеа'),
            dtos.DiagnosisCreateSchema(name='Розацеа'),
            entities.Diagnosis(id=1, name='Розацеа')
        )

    ])
    def test__create_new_diagnosis(self, entity, dto, returned_entity, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = returned_entity

        # Call
        result = service.create(new_diagnosis_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_name(dto.name), call.add(entity)]
        assert result == returned_entity

    @pytest.mark.parametrize("entity, dto", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.DiagnosisCreateSchema(name='Розацеа')
        ),
    ])
    def test__create_existing_diagnosis(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = entity

        # Call and Assert
        with pytest.raises(errors.DiagnosisAlreadyExists):
            service.create(new_diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("entity, dto, returned_entity", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.DiagnosisUpdateSchema(id=1, name='Атопический дерматит'),
            entities.Diagnosis(id=1, name='Атопический дерматит')
        ),
    ])
    def test__change_existing_diagnosis(self, entity, dto, returned_entity, service,
                                        repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call
        result = service.change(new_diagnosis_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id)]
        assert result == returned_entity

    @pytest.mark.parametrize("dto", [
        dtos.DiagnosisUpdateSchema(id=1, name='Псориаз')
    ])
    def test__change_non_existing_diagnosis(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.change(new_diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("entity, dto", [
        (entities.Diagnosis(id=1, name='Розацеа'),
         dtos.DiagnosisUpdateSchema(id=1, name='Розацеа')),
    ])
    def test__change_existing_diagnosis_with_same_name(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity

        # Call and Assert
        with pytest.raises(errors.DiagnosisAlreadyExists):
            service.change(new_diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]


class TestDelete:
    @pytest.mark.parametrize("entity, dto", [
        (entities.Diagnosis(id=1, name='Розацеа'), dtos.DiagnosisDeleteSchema(id=1))
    ])
    def test__delete_existing_diagnosis(self, entity, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = entity
        repo.remove.return_value = entity

        # Call
        result = service.delete(diagnosis_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(dto.id), call.remove(entity)]
        assert result == entity

    @pytest.mark.parametrize("dto", [
        dtos.DiagnosisDeleteSchema(id=1)
    ])
    def test__delete_non_existing_diagnosis(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.delete(diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]
