from unittest.mock import Mock, call

import pytest

from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.DiagnosesRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.Diagnosis:
    return services.Diagnosis(diagnoses_repo=repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGet:

    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.Diagnosis(id=1, name='Розацеа', ),
            dtos.Diagnosis(id=1, name='Розацеа', )
        )
    ])
    def test__get_diagnosis(self, repo_output, service_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get(diagnosis_id=service_output.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(service_output.id)]
        assert result == service_output

    @pytest.mark.parametrize("repo_output", [entities.Diagnosis(id=1, name='Розацеа')])
    def test_diagnosis_not_found(self, repo_output, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.get(diagnosis_id=repo_output.id)

        assert repo.method_calls == [call.fetch_by_id(repo_output.id)]


class TestAdd:
    @pytest.mark.parametrize("added_entity, input_dto, repo_output, service_output", [
        (
            entities.Diagnosis(name='Розацеа'),
            dtos.NewDiagnosisInfo(name='Розацеа'),
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.Diagnosis(id=1, name='Розацеа')
        )
    ])
    def test__add_new_diagnosis(self, added_entity, input_dto, repo_output,
                                service_output, service, repo):
        # Setup
        repo.fetch_by_name.return_value = None
        repo.add.return_value = repo_output

        # Call
        result = service.add(new_diagnosis_info=input_dto)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_name(input_dto.name),
            call.add(added_entity)
        ]
        assert result == service_output

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.NewDiagnosisInfo(name='Розацеа')
        ),
    ])
    def test__add_existing_diagnosis(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_name.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.DiagnosisAlreadyExists):
            service.add(new_diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_name(dto.name)]


class TestChange:
    @pytest.mark.parametrize("repo_output, new_info, service_output", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.Diagnosis(id=1, name='Атопический дерматит'),
            dtos.Diagnosis(id=1, name='Атопический дерматит')
        ),
    ])
    def test__change_existing_diagnosis(self, repo_output, new_info, service_output,
                                        service, repo):
        # Setup
        repo.fetch_by_id.return_value = repo_output
        repo.fetch_by_name.return_value = None

        # Call
        result = service.change(new_diagnosis_info=new_info)

        # Assert
        assert repo.method_calls == [
            call.fetch_by_id(new_info.id), call.fetch_by_name(new_info.name)]
        assert result == service_output

    @pytest.mark.parametrize("dto", [
        dtos.Diagnosis(id=1, name='Псориаз')
    ])
    def test__change_non_existing_diagnosis(self, dto, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.change(new_diagnosis_info=dto)

        assert repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("repo_fetch_by_id_output, repo_fetch_by_name_output, dto", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            entities.Diagnosis(id=2, name='Атопический дерматит'),
            dtos.Diagnosis(id=1, name='Атопический дерматит')
        ),
    ])
    def test__change_existing_diagnosis_with_same_name(
        self, repo_fetch_by_id_output, repo_fetch_by_name_output, dto, service, repo
    ):
        # Setup
        repo.fetch_by_id.return_value = repo_fetch_by_id_output
        repo.fetch_by_name.return_value = repo_fetch_by_name_output

        # Call and Assert
        with pytest.raises(errors.DiagnosisAlreadyExists):
            service.change(new_diagnosis_info=dto)

        assert repo.method_calls == [
            call.fetch_by_id(dto.id),
            call.fetch_by_name(dto.name)
        ]


class TestDelete:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.Diagnosis(id=1, name='Розацеа'),
            dtos.Diagnosis(id=1, name='Розацеа')
        )

    ])
    def test__delete(self, repo_output, service_output, service, repo):
        # Setup
        diagnosis_id = 1
        repo.fetch_by_id.return_value = repo_output
        repo.remove.return_value = repo_output

        # Call
        result = service.delete(diagnosis_id=diagnosis_id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(diagnosis_id),
                                     call.remove(repo_output)]
        assert result == service_output

    def test__diagnosis_not_found(self, service, repo):
        # Setup
        diagnosis_id = 1
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.delete(diagnosis_id=diagnosis_id)

        assert repo.method_calls == [call.fetch_by_id(diagnosis_id)]
