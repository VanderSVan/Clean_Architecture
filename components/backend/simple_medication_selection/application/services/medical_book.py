from typing import Sequence

from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class MedicalBook:
    def __init__(self,
                 medical_books_repo: interfaces.MedicalBooksRepo,
                 patients_repo: interfaces.PatientsRepo,
                 diagnoses_repo: interfaces.DiagnosesRepo
                 ) -> None:
        self.med_books_repo = medical_books_repo
        self.patients_repo = patients_repo
        self.diagnoses_repo = diagnoses_repo

    @register_method
    @validate_call
    def get(self, medical_book_id: int) -> entities.MedicalBook:

        medical_book: entities.MedicalBook = (
            self.med_books_repo.fetch_by_id(medical_book_id)
        )
        if not medical_book:
            raise errors.MedicalBookNotFound(id=medical_book_id)

        return medical_book

    @register_method
    @validate_call
    def get_patient_med_books(self,
                              patient_id: int,
                              *,
                              limit: int = 10,
                              offset: int = 0
                              ) -> Sequence[entities.MedicalBook | None]:

        return self.med_books_repo.fetch_by_patient(patient_id, limit, offset)

    @register_method
    @validate_call
    def add(self,
            new_med_book_info: dtos.MedicalBookCreateSchema
            ) -> entities.MedicalBook:

        patient: entities.Patient = (
            self.patients_repo.fetch_by_id(new_med_book_info.patient_id)
        )
        if not patient:
            raise errors.PatientNotFound(id=new_med_book_info.patient_id)

        diagnosis: entities.Diagnosis = (
            self.diagnoses_repo.fetch_by_id(new_med_book_info.diagnosis_id)
        )
        if not diagnosis:
            raise errors.DiagnosisNotFound(id=new_med_book_info.diagnosis_id)

        medical_book: entities.MedicalBook = (
            new_med_book_info.create_obj(entities.MedicalBook)
        )

        return self.med_books_repo.add(medical_book)

    @register_method
    @validate_call
    def change(self,
               new_med_book_info: dtos.MedicalBookUpdateSchema
               ) -> entities.MedicalBook:

        medical_book: entities.MedicalBook = (
            self.med_books_repo.fetch_by_id(new_med_book_info.id)
        )
        if not medical_book:
            raise errors.MedicalBookNotFound(id=new_med_book_info.id)

        if new_med_book_info.patient_id:
            patient: entities.Patient = (
                self.patients_repo.fetch_by_id(new_med_book_info.patient_id)
            )
            if not patient:
                raise errors.PatientNotFound(id=new_med_book_info.patient_id)

        if new_med_book_info.diagnosis_id:
            diagnosis: entities.Diagnosis = (
                self.diagnoses_repo.fetch_by_id(new_med_book_info.diagnosis_id)
            )
            if not diagnosis:
                raise errors.DiagnosisNotFound(id=new_med_book_info.diagnosis_id)

        return new_med_book_info.populate_obj(medical_book)

    def delete(self, med_book_id: int) -> entities.MedicalBook:

        medical_book: entities.MedicalBook = (
            self.med_books_repo.fetch_by_id(med_book_id)
        )
        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return self.med_books_repo.remove(medical_book)
