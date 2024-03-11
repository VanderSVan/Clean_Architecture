from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors, interfaces,
                                                     services)


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
class TestGet:
    @pytest.mark.parametrize("returned_entity", [
        entities.MedicalBook(id=1, title_history='title', history='history',
                             patient_id=1, diagnosis_id=1),
    ])
    def test__get_existing_medical_book(self, returned_entity, service, med_books_repo,
                                        patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = returned_entity

        # Call
        result = service.get(medical_book_id=returned_entity.id)

        # Assert
        assert med_books_repo.method_calls == [call.fetch_by_id(returned_entity.id)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == returned_entity

    def test_get_non_existing_medical_book(self, service, med_books_repo, patients_repo,
                                           diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get(medical_book_id=1)

        assert med_books_repo.method_calls == [call.fetch_by_id(1)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []


class TestGetPatientMedBooks:
    @pytest.mark.parametrize("returned_entity", [
        entities.MedicalBook(
            id=1,
            title_history='title',
            history='history',
            patient_id=1,
            diagnosis_id=1,
            symptoms=[entities.Symptom(id=1, name='symptom1')],
            item_reviews=[entities.ItemReview(
                id=1,
                item_id=1,
                is_helped=True,
                item_rating=8,
                item_count=3,
                usage_period=7776000)
            ]
        ),
    ])
    def test__get_patient_medical_books(self, returned_entity, service, med_books_repo,
                                        patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_patient.return_value = [returned_entity]
        default_limit = 10
        default_offset = 0

        # Call
        result = service.get_patient_med_books(patient_id=returned_entity.patient_id)

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_patient(
                returned_entity.patient_id, default_limit, default_offset
            )
        ]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == [returned_entity]


class TestAdd:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.MedicalBook(title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.MedicalBookCreateSchema(title_history='title', history='history',
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
        dtos.MedicalBookCreateSchema(title_history='title', history='history',
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
        dtos.MedicalBookCreateSchema(title_history='title', history='history',
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
            dtos.MedicalBookUpdateSchema(id=2, title_history='blabla',
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
        dtos.MedicalBookUpdateSchema(id=10001, title_history='title',
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
            dtos.MedicalBookUpdateSchema(id=1, patient_id=10001, )
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
            dtos.MedicalBookUpdateSchema(id=1, patient_id=10, diagnosis_id=10001, )
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
    @pytest.mark.parametrize("existing_entity, dto, removed_entity", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            dtos.MedicalBookDeleteSchema(id=1),
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1)
        )
    ])
    def test__delete_med_book(self, existing_entity, dto, removed_entity, service,
                              med_books_repo, patients_repo, diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        med_books_repo.remove.return_value = removed_entity

        # Call
        result = service.delete(medical_book_info=dto)

        # Assert
        assert med_books_repo.method_calls == [call.fetch_by_id(existing_entity.id),
                                               call.remove(existing_entity)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == removed_entity

    @pytest.mark.parametrize("dto", [
        dtos.MedicalBookDeleteSchema(id=10001)
    ])
    def test__medical_book_not_found(self, dto, service, med_books_repo, patients_repo,
                                     diagnoses_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.delete(medical_book_info=dto)

        assert med_books_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
