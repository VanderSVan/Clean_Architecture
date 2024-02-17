from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Patient:
    def __init__(self, patients_repo: interfaces.PatientsRepo):
        self.patients_repo = patients_repo

    @register_method
    @validate_call
    def get(self, patient_id: int) -> entities.Patient:
        patient = self.patients_repo.fetch_by_id(patient_id)

        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        return patient

    @register_method
    @validate_call
    def create(self, new_patient_info: dtos.PatientCreateSchema) -> entities.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
        )

        if patient:
            raise errors.PatientAlreadyExists(nickname=new_patient_info.nickname)

        new_patient: entities.Patient = new_patient_info.create_obj(entities.Patient)

        return self.patients_repo.add(new_patient)

    @register_method
    @validate_call
    def update(self, new_patient_info: dtos.PatientUpdateSchema) -> entities.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
        )

        if not patient:
            raise errors.PatientNotFound(id=new_patient_info.id)

        updated_patient: entities.Patient = new_patient_info.update_obj(patient)

        return self.patients_repo.update(updated_patient)

    @register_method
    @validate_call
    def delete(self, patient_info: dtos.PatientDeleteSchema) -> entities.Patient:
        patient = self.patients_repo.fetch_by_id(patient_info.id)

        if not patient:
            raise errors.PatientNotFound(id=patient_info.id)

        return self.patients_repo.remove(patient)
