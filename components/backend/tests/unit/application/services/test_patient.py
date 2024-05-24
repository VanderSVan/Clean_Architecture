from unittest.mock import Mock, call, patch

import pytest

from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def patients_repo() -> Mock:
    return Mock(interfaces.PatientsRepo)


@pytest.fixture(scope='function')
def medical_books_repo() -> Mock:
    return Mock(interfaces.MedicalBooksRepo)


@pytest.fixture(scope='function')
def service(patients_repo, medical_books_repo) -> services.Patient:
    return services.Patient(patients_repo=patients_repo,
                            medical_books_repo=medical_books_repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGet:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="сухая", about="About Girl", phone='1234567890'),
            dtos.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                         skin_type="сухая", about="About Girl", phone='1234567890')

        )
    ])
    def test__get(self, repo_output, service_output, service, patients_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get(patient_id=repo_output.id)

        # Assert
        assert patients_repo.method_calls == [call.fetch_by_id(repo_output.id)]
        assert result == service_output

    def test__patient_not_found(self, service, patients_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.get(patient_id=1)

        assert patients_repo.method_calls == [call.fetch_by_id(1)]


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
    def test__find(self, gender, age_from, age_to, skin_type,
                   repo_method, service, patients_repo):
        # Setup
        filter_params = schemas.FindPatients(
            gender=gender, age_from=age_from, age_to=age_to, skin_type=skin_type
        )
        repo_output = [
            entities.Patient(id=1, nickname="some_nickname", gender="female", age=25,
                             skin_type="сухая", about="About me", phone='1234567890')
        ]
        service_output = [
            dtos.Patient(id=1, nickname="some_nickname", gender="female", age=25,
                         skin_type="сухая", about="About me", phone='1234567890')
        ]
        getattr(patients_repo, repo_method).return_value = repo_output

        # Call
        result = service.find(filter_params=filter_params)

        # Assert
        getattr(patients_repo, repo_method).assert_called_once_with(filter_params)
        assert result == service_output


class TestAdd:
    @pytest.mark.parametrize("input_dto, repo_output, service_output", [
        (
            dtos.NewPatientInfo(nickname="SomeGirl", gender="female", age=18,
                                skin_type="жирная", about="About Girl",
                                phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            dtos.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                         skin_type="жирная", about="About Girl", phone='1234567890')
        )
    ])
    def test__add(self, input_dto, repo_output, service_output, service, patients_repo):
        # Setup
        patients_repo.fetch_by_nickname.return_value = None
        patients_repo.add.return_value = repo_output

        # Call
        result = service.add(new_patient_info=input_dto)

        # Assert
        assert patients_repo.method_calls == [call.fetch_by_nickname(input_dto.nickname),
                                              call.add(
                                                  entities.Patient(**input_dto.dict()))]
        assert result == service_output

    @pytest.mark.parametrize("input_dto, repo_output", [
        (
            dtos.NewPatientInfo(nickname="SomeGirl", gender="female", age=18,
                                skin_type="жирная", about="About Girl",
                                phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890')
        )
    ])
    def test__patient_already_exists(self, input_dto, repo_output, service,
                                     patients_repo):
        # Setup
        patients_repo.fetch_by_nickname.return_value = repo_output

        # Call and Assert
        with pytest.raises(errors.PatientAlreadyExists):
            service.add(new_patient_info=input_dto)

        assert patients_repo.method_calls == [call.fetch_by_nickname(input_dto.nickname)]


class TestChange:

    @pytest.mark.parametrize("input_dto, repo_output, service_output", [
        (
            dtos.UpdatedPatientInfo(id=1, nickname="SomeMan", gender="male", age=18,
                                    skin_type="жирная", about="About Man",
                                    phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            dtos.Patient(id=1, nickname="SomeMan", gender="male", age=18,
                         skin_type="жирная", about="About Man", phone='1234567890')
        )
    ])
    def test__change(self, input_dto, repo_output, service_output, service,
                     patients_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = repo_output
        patients_repo.fetch_by_nickname.return_value = None

        # Call
        result = service.change(new_patient_info=input_dto)

        # Assert
        assert patients_repo.method_calls == [
            call.fetch_by_id(input_dto.id),
            call.fetch_by_nickname(input_dto.nickname)
        ]
        assert result == service_output

    @pytest.mark.parametrize("input_dto", [
        dtos.UpdatedPatientInfo(id=1, nickname="SomeMan", gender="male", age=18,
                                skin_type="жирная", about="About Man",
                                phone='1234567890')
    ])
    def test__patient_not_found(self, input_dto, service, patients_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.change(new_patient_info=input_dto)

        assert patients_repo.method_calls == [call.fetch_by_id(input_dto.id)]

    @pytest.mark.parametrize("input_dto, fetch_by_id_output, fetch_by_nickname_output", [
        (
            dtos.UpdatedPatientInfo(id=1, nickname="SomeMan", gender="male", age=18,
                                    skin_type="жирная", about="About Man",
                                    phone='1234567890'),
            entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
            entities.Patient(id=2, nickname="SomeMan", gender="male", age=28,
                             skin_type="сухая", about="About Man 2", phone='9874561230')
        )
    ])
    def test__nickname_already_exists(self, input_dto, fetch_by_id_output,
                                      fetch_by_nickname_output, service, patients_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = fetch_by_id_output
        patients_repo.fetch_by_nickname.return_value = fetch_by_nickname_output

        # Call and Assert
        with pytest.raises(errors.PatientAlreadyExists):
            service.change(new_patient_info=input_dto)

        assert patients_repo.method_calls == [
            call.fetch_by_id(input_dto.id),
            call.fetch_by_nickname(input_dto.nickname)
        ]


class TestDelete:
    @pytest.mark.parametrize(
        "patient_id, fetch_by_id_output, remove_output, service_output, new_patient_info,"
        "new_patient",
        [
            (
                1,
                entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                                 skin_type="жирная", about="About Girl",
                                 phone='1234567890'),
                entities.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                                 skin_type="жирная", about="About Girl",
                                 phone='1234567890'),
                dtos.Patient(id=1, nickname="SomeGirl", gender="female", age=18,
                             skin_type="жирная", about="About Girl", phone='1234567890'),
                dtos.NewPatientInfo(
                    nickname="Anonymous-986f541d-1d9a-46cf-aace-78befb3e74a2",
                    gender="female", age=18, skin_type="жирная"
                ),
                entities.Patient(
                    id=2, nickname="Anonymous-986f541d-1d9a-46cf-aace-78befb3e74a2",
                    gender="female", age=18, skin_type="жирная"
                )
            )
        ]
    )
    def test__delete(self, patient_id, fetch_by_id_output, remove_output, service_output,
                     new_patient_info, new_patient, service, patients_repo,
                     medical_books_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = fetch_by_id_output
        patients_repo.fetch_by_nickname.return_value = None
        patients_repo.add.return_value = new_patient
        patients_repo.remove.return_value = remove_output

        medical_books_repo.fetch_by_patient.return_value = [
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            entities.MedicalBook(id=2, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=2)
        ]

        mock_uuid4: str = new_patient_info.nickname.lstrip("Anonymous-")
        with patch('uuid.uuid4', return_value=mock_uuid4):
            # Call
            result = service.delete(patient_id=patient_id)

        # Assert
        assert patients_repo.method_calls == [
            call.fetch_by_id(patient_id),
            call.fetch_by_nickname(new_patient_info.nickname),
            call.add(entities.Patient(**new_patient_info.dict())),
            call.remove(fetch_by_id_output)
        ]
        assert result == service_output

    def test__patient_not_found(self, service, patients_repo):
        # Setup
        patient_id = 1
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.delete(patient_id=patient_id)

        assert patients_repo.method_calls == [call.fetch_by_id(patient_id)]
