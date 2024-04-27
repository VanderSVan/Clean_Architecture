from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def repo() -> Mock:
    return Mock(interfaces.PatientsRepo)


@pytest.fixture(scope='function')
def service(repo) -> services.Patient:
    return services.Patient(patients_repo=repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGet:
    @pytest.mark.parametrize("returned_entity", [
        entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                         skin_type="сухая", about="About Girl", phone='1234567890')
    ])
    def test__get_patient(self, returned_entity, service, repo):
        # Setup
        repo.fetch_by_id.return_value = returned_entity

        # Call
        result = service.get(patient_id=returned_entity.id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(returned_entity.id)]
        assert result == returned_entity

    def test__get_non_existing_patient(self, service, repo):
        # Setup
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.get(patient_id=1)

        assert repo.method_calls == [call.fetch_by_id(1)]


class TestFind:
    @pytest.mark.parametrize(
        "gender, age_from, age_to, skin_type, repo_method",
        [
            ('female', 18, 40, 'сухая', 'fetch_by_gender_age_and_skin_type'),
            ('female', None, 40, 'сухая', 'fetch_by_gender_age_and_skin_type'),
            ('female', 18, None, 'сухая', 'fetch_by_gender_age_and_skin_type'),

            (None, 18, 40, 'сухая', 'fetch_by_age_and_skin_type'),
            (None, None, 40, 'сухая', 'fetch_by_age_and_skin_type'),
            (None, 18, None, 'сухая', 'fetch_by_age_and_skin_type'),

            ('female', None, None, 'сухая', 'fetch_by_gender_and_skin_type'),

            ('female', 18, 40, None, 'fetch_by_gender_and_age'),
            ('female', None, 40, None, 'fetch_by_gender_and_age'),
            ('female', 18, None, None, 'fetch_by_gender_and_age'),

            (None, None, None, 'сухая', 'fetch_by_skin_type'),

            (None, 18, 40, None, 'fetch_by_age'),
            (None, None, 40, None, 'fetch_by_age'),
            (None, 18, None, None, 'fetch_by_age'),

            ('female', None, None, None, 'fetch_by_gender'),

            (None, None, None, None, 'fetch_all'),
        ]
    )
    def test__find_patients(self, gender, age_from, age_to, skin_type,
                            repo_method, service, repo):
        # Setup
        filter_params = schemas.FindPatients(
            gender=gender, age_from=age_from, age_to=age_to, skin_type=skin_type
        )
        repo_output = [
            entities.Patient(id=1, nickname="some_nickname", gender="female", age=25,
                             skin_type="сухая", about="About me", phone='1234567890')
        ]
        getattr(repo, repo_method).return_value = repo_output

        # Call
        result = service.find(filter_params=filter_params)

        # Assert
        getattr(repo, repo_method).assert_called_once_with(filter_params)
        assert result == repo_output


class TestCreate:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.Patient(nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            dtos.PatientCreateSchema(nickname="SomeGirl", gender="female", age=18,
                                     skin_type="жирная", about="About Girl",
                                     phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890')
        )
    ])
    def test__create_new_patient(self, new_entity, dto, created_entity, service, repo):
        # Setup
        repo.fetch_by_nickname.return_value = None
        repo.add.return_value = created_entity

        # Call
        result = service.create(new_patient_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_nickname(dto.nickname),
                                     call.add(new_entity)]
        assert result == created_entity

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.Patient(id=1, nickname="SomeGirl", gender="male", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            dtos.PatientCreateSchema(nickname="SomeGirl", gender="male", age=28,
                                     skin_type="комбинированная", about="About Girl",
                                     phone='9874561230'),
        )
    ])
    def test__patient_already_exists(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_nickname.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.PatientAlreadyExists):
            service.create(new_patient_info=dto)

        assert repo.method_calls == [call.fetch_by_nickname(dto.nickname)]


class TestChange:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            dtos.PatientUpdateSchema(id=1, nickname="SomeMan", gender="male", age=18,
                                     skin_type="жирная", about="About Man",
                                     phone='1234567890'),
            entities.Patient(id=1, nickname="SomeMan", gender="male", age=18,
                             skin_type="жирная", about="About Man", phone='1234567890')
        )
    ])
    def test__change_existing_patient(self, existing_entity, dto, updated_entity,
                                      service, repo):
        # Setup
        repo.fetch_by_nickname.return_value = existing_entity

        # Call
        result = service.change(new_patient_info=dto)

        # Assert
        assert repo.method_calls == [call.fetch_by_nickname(dto.nickname)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.PatientUpdateSchema(id=1, nickname="SomeMan", gender="male", age=18,
                                 skin_type="жирная", about="About Man",
                                 phone='1234567890')
    ])
    def test__patient_does_not_exist(self, dto, service, repo):
        # Setup
        repo.fetch_by_nickname.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.change(new_patient_info=dto)

        assert repo.method_calls == [call.fetch_by_nickname(dto.nickname)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.Patient(id=1, nickname="SomeMan", gender="male", age=38,
                             skin_type="жирная", about="About Man", phone='85245691730'),
            dtos.PatientUpdateSchema(id=1, nickname="SomeMan", gender="male", age=18,
                                     skin_type="жирная", about="About Man2",
                                     phone='1234567890')
        )
    ])
    def test__nickname_already_exists(self, existing_entity, dto, service, repo):
        # Setup
        repo.fetch_by_nickname.return_value = existing_entity

        # Call and Assert
        with pytest.raises(errors.PatientAlreadyExists):
            service.change(new_patient_info=dto)

        assert repo.method_calls == [call.fetch_by_nickname("SomeMan")]


class TestDelete:
    @pytest.mark.parametrize("existing_entity, removed_entity", [
        (
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="сухая", about="About Girl", phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="сухая", about="About Girl", phone='1234567890')
        )
    ])
    def test__delete_existing_patient(self, existing_entity, removed_entity, service,
                                      repo):
        # Setup
        patient_id = 1
        repo.fetch_by_id.return_value = existing_entity
        repo.remove.return_value = removed_entity

        # Call
        result = service.delete(patient_id=patient_id)

        # Assert
        assert repo.method_calls == [call.fetch_by_id(existing_entity.id),
                                     call.remove(removed_entity)]
        assert result == removed_entity

    def test__delete_non_existing_patient(self, service, repo):
        # Setup
        patient_id = 1
        repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.delete(patient_id=patient_id)

        assert repo.method_calls == [call.fetch_by_id(patient_id)]
