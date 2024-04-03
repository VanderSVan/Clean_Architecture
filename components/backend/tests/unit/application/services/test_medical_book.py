from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def med_books_repo() -> Mock:
    return Mock(interfaces.MedicalBooksRepo)


@pytest.fixture(scope='function')
def patients_repo() -> Mock:
    return Mock(interfaces.PatientsRepo)


@pytest.fixture(scope='function')
def diagnoses_repo() -> Mock:
    return Mock(interfaces.DiagnosesRepo)


@pytest.fixture(scope='function')
def service(med_books_repo,
            patients_repo,
            diagnoses_repo
            ) -> services.MedicalBook:
    return services.MedicalBook(medical_books_repo=med_books_repo,
                                patients_repo=patients_repo,
                                diagnoses_repo=diagnoses_repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "med_book_id, include_symptoms, include_reviews, repo_method", [
        (1, True, True, 'fetch_by_id_with_symptoms_and_reviews'),
        (1, True, False, 'fetch_by_id_with_symptoms'),
        (1, False, True, 'fetch_by_id_with_reviews'),
        (1, False, False, 'fetch_by_id')
    ]
)
class TestGetMedBook:

    def test__get_med_book(self, med_book_id, include_symptoms,
                           include_reviews, repo_method, service,
                           med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        returned_entity = entities.MedicalBook(
            id=1, title_history='title', history='history', patient_id=1, diagnosis_id=1
        )
        getattr(med_books_repo, repo_method).return_value = returned_entity

        # Call
        result = service.get_med_book(med_book_id=med_book_id,
                                      include_symptoms=include_symptoms,
                                      include_reviews=include_reviews)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(med_book_id)
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == returned_entity

    def test_medical_book_not_found(self, med_book_id, include_symptoms,
                                    include_reviews, repo_method, service,
                                    med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        getattr(med_books_repo, repo_method).return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get_med_book(med_book_id=med_book_id,
                                 include_symptoms=include_symptoms,
                                 include_reviews=include_reviews)

        getattr(med_books_repo, repo_method).assert_called_once_with(med_book_id)
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []


class TestFindMedBooks:

    @pytest.mark.parametrize("filter_params, repo_method", [
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True, diagnosis_id=1,
                                            symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False, diagnosis_id=1,
                                            symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True, diagnosis_id=1,
                                            symptom_ids=[1, 2]),
            'fetch_by_patient_helped_status_diagnosis_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False, diagnosis_id=1,
                                            symptom_ids=[1, 2]),
            'fetch_by_patient_helped_status_diagnosis_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True, diagnosis_id=1),
            'fetch_by_patient_helped_status_and_diagnosis'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False,
                                            diagnosis_id=1),
            'fetch_by_patient_helped_status_and_diagnosis'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True,
                                            symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_patient_helped_status_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False,
                                            symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_patient_helped_status_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True,
                                            symptom_ids=[1, 2]),
            'fetch_by_patient_helped_status_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False,
                                            symptom_ids=[1, 2]),
            'fetch_by_patient_helped_status_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=True),
            'fetch_by_patient_and_helped_status'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, is_helped=False),
            'fetch_by_patient_and_helped_status'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, diagnosis_id=1,
                                            symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_patient_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, diagnosis_id=1,
                                            symptom_ids=[1, 2]),
            'fetch_by_patient_diagnosis_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, diagnosis_id=1),
            'fetch_by_patient_and_diagnosis'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, symptom_ids=[1, 2],
                                            match_all_symptoms=True),
            'fetch_by_patient_with_matching_all_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1, symptom_ids=[1, 2]),
            'fetch_by_patient_and_symptoms'
        ),
        (
            schemas.FindPatientMedicalBooks(patient_id=1),
            'fetch_by_patient'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True, diagnosis_id=1,
                                     symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False, diagnosis_id=1,
                                     symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True, diagnosis_id=1, symptom_ids=[1, 2]),
            'fetch_by_helped_status_diagnosis_and_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False, diagnosis_id=1, symptom_ids=[1, 2]),
            'fetch_by_helped_status_diagnosis_and_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True, diagnosis_id=1),
            'fetch_by_helped_status_and_diagnosis'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False, diagnosis_id=1),
            'fetch_by_helped_status_and_diagnosis'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True, symptom_ids=[1, 2],
                                     match_all_symptoms=True),
            'fetch_by_helped_status_with_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False, symptom_ids=[1, 2],
                                     match_all_symptoms=True),
            'fetch_by_helped_status_with_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True, symptom_ids=[1, 2]),
            'fetch_by_helped_status_and_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False, symptom_ids=[1, 2]),
            'fetch_by_helped_status_and_symptoms'
        ),
        (
            schemas.FindMedicalBooks(is_helped=True),
            'fetch_by_helped_status'
        ),
        (
            schemas.FindMedicalBooks(is_helped=False),
            'fetch_by_helped_status'
        ),
        (
            schemas.FindMedicalBooks(diagnosis_id=1, symptom_ids=[1, 2],
                                     match_all_symptoms=True),
            'fetch_by_diagnosis_with_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(diagnosis_id=1, symptom_ids=[1, 2]),
            'fetch_by_diagnosis_and_symptoms'
        ),
        (
            schemas.FindMedicalBooks(diagnosis_id=1),
            'fetch_by_diagnosis'
        ),
        (
            schemas.FindMedicalBooks(symptom_ids=[1, 2], match_all_symptoms=True),
            'fetch_by_matching_all_symptoms'
        ),
        (
            schemas.FindMedicalBooks(symptom_ids=[1, 2]),
            'fetch_by_symptoms'
        ),
        (
            schemas.FindMedicalBooks(),
            'fetch_all'
        )
    ])
    def test_find_med_books(self, filter_params, repo_method, service,
                            med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        returned_entities = [
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1)
        ]
        getattr(med_books_repo, repo_method).return_value = returned_entities

        # Call
        result = service.find_med_books(filter_params)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(filter_params)
        assert result == returned_entities
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []


class TestAdd:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.MedicalBook(title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.NewMedicalBookInfo(title_history='title', history='history',
                                    patient_id=1, diagnosis_id=1),
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1)
        )
    ])
    def test__add_new_med_book(self, new_entity, dto, created_entity, service,
                               med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        med_books_repo.add.return_value = created_entity

        # Call
        result = service.add(new_med_book_info=dto)

        # Assert
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert med_books_repo.method_calls == [call.add(new_entity)]
        assert result == created_entity

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=10001, diagnosis_id=1)
    ])
    def test__patient_not_found(self, dto, service, med_books_repo, patients_repo,
                                diagnoses_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == []
        assert med_books_repo.method_calls == []

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=1, diagnosis_id=10001)
    ])
    def test__diagnosis_not_found(self, dto, service, med_books_repo, patients_repo,
                                  diagnoses_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert med_books_repo.method_calls == []


class TestChange:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                        patient_id=5, diagnosis_id=101),
            entities.MedicalBook(id=2, title_history='blabla', history='history',
                                 patient_id=5, diagnosis_id=101)
        )
    ])
    def test__change_med_book(self, existing_entity, dto, updated_entity, service,
                              med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=5, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=101, name='Diagnosis'
        )

        # Call
        result = service.change(new_med_book_info=dto)

        # Assert
        assert med_books_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.UpdatedMedicalBookInfo(id=10001, title_history='title',
                                    patient_id=1, diagnosis_id=1)
    ])
    def test__med_book_not_found(self, dto, service, med_books_repo,
                                 patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.UpdatedMedicalBookInfo(id=1, patient_id=10001, )
        )
    ])
    def test__patient_not_found(self, existing_entity, dto, service, med_books_repo,
                                patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.UpdatedMedicalBookInfo(id=1, patient_id=10, diagnosis_id=10001, )
        )
    ])
    def test__diagnosis_not_found(self, existing_entity, dto, service, med_books_repo,
                                  patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=10, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]


class TestDelete:
    @pytest.mark.parametrize("existing_entity, removed_entity", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1)
        )
    ])
    def test__delete_med_book(self, existing_entity, removed_entity, service,
                              med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = existing_entity
        med_books_repo.remove.return_value = removed_entity

        # Call
        result = service.delete(med_book_id=med_book_id)

        # Assert
        assert med_books_repo.method_calls == [call.fetch_by_id(existing_entity.id),
                                               call.remove(existing_entity)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == removed_entity

    def test__medical_book_not_found(self, service, med_books_repo, patients_repo,
                                     diagnoses_repo):
        # Setup
        med_book_id = 10001
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.delete(med_book_id=med_book_id)

        assert med_books_repo.method_calls == [call.fetch_by_id(med_book_id)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
