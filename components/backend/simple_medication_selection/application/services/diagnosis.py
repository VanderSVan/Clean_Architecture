from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Diagnosis:
    def __init__(self, diagnoses_repo: interfaces.DiagnosesRepo):
        self.diagnoses_repo = diagnoses_repo

    @register_method
    @validate_call
    def get(self, diagnosis_id: int) -> entities.Diagnosis:
        diagnosis = self.diagnoses_repo.fetch_by_id(diagnosis_id)

        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)

        return diagnosis

    @register_method
    @validate_call
    def create(self,
               new_diagnosis_info: dtos.DiagnosisCreateSchema
               ) -> entities.Diagnosis:

        diagnosis: entities.Diagnosis = (
            self.diagnoses_repo.fetch_by_name(new_diagnosis_info.name)
        )

        if diagnosis:
            raise errors.DiagnosisAlreadyExists(name=new_diagnosis_info.name)

        new_diagnosis: entities.Diagnosis = (
            new_diagnosis_info.create_obj(entities.Diagnosis)
        )
        return self.diagnoses_repo.add(new_diagnosis)

    @register_method
    @validate_call
    def change(self,
               new_diagnosis_info: dtos.DiagnosisUpdateSchema
               ) -> entities.Diagnosis:

        diagnosis: entities.Diagnosis = (
            self.diagnoses_repo.fetch_by_id(new_diagnosis_info.id)
        )
        if not diagnosis:
            raise errors.DiagnosisNotFound(id=new_diagnosis_info.id)

        if new_diagnosis_info.name == diagnosis.name:
            raise errors.DiagnosisAlreadyExists(name=new_diagnosis_info.name)

        return new_diagnosis_info.populate_obj(diagnosis)

    @register_method
    @validate_call
    def delete(self, diagnosis_id: int) -> entities.Diagnosis:
        diagnosis = self.diagnoses_repo.fetch_by_id(diagnosis_id)

        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)

        return self.diagnoses_repo.remove(diagnosis)
