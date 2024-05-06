from typing import Sequence

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Diagnosis:
    def __init__(self, diagnoses_repo: interfaces.DiagnosesRepo) -> None:
        self.diagnoses_repo = diagnoses_repo

    @register_method
    @validate_arguments
    def get(self, diagnosis_id: int) -> dtos.Diagnosis:
        diagnosis = self.diagnoses_repo.fetch_by_id(diagnosis_id)

        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)

        return dtos.Diagnosis.from_orm(diagnosis)

    @register_method
    @validate_arguments
    def find(self, filter_params: schemas.FindDiagnoses) -> list[dtos.Diagnosis | None]:
        if filter_params.keywords:
            found_diagnoses: Sequence[entities.Diagnosis | None] = (
                self.diagnoses_repo.search_by_name(filter_params)
            )
        else:
            found_diagnoses: Sequence[entities.Diagnosis | None] = (
                self.diagnoses_repo.fetch_all(filter_params)
            )
        return [dtos.Diagnosis.from_orm(diagnosis) for diagnosis in found_diagnoses]

    @register_method
    @validate_arguments
    def add(self, new_diagnosis_info: dtos.NewDiagnosisInfo) -> dtos.Diagnosis:

        diagnosis: entities.Diagnosis | None = (
            self.diagnoses_repo.fetch_by_name(new_diagnosis_info.name)
        )

        if diagnosis:
            raise errors.DiagnosisAlreadyExists(name=new_diagnosis_info.name)

        new_diagnosis: entities.Diagnosis = (
            new_diagnosis_info.create_obj(entities.Diagnosis)
        )
        added_diagnosis: entities.Diagnosis = self.diagnoses_repo.add(new_diagnosis)
        return dtos.Diagnosis.from_orm(added_diagnosis)

    @register_method
    @validate_arguments
    def change(self, new_diagnosis_info: dtos.Diagnosis) -> dtos.Diagnosis:

        diagnosis: entities.Diagnosis = (
            self.diagnoses_repo.fetch_by_id(new_diagnosis_info.id)
        )
        if not diagnosis:
            raise errors.DiagnosisNotFound(id=new_diagnosis_info.id)

        diagnosis_with_same_name: entities.Diagnosis | None = (
            self.diagnoses_repo.fetch_by_name(new_diagnosis_info.name)
        )
        if diagnosis_with_same_name and diagnosis_with_same_name.id != diagnosis.id:
            raise errors.DiagnosisAlreadyExists(name=new_diagnosis_info.name)

        updated_diagnosis: entities.Diagnosis = new_diagnosis_info.populate_obj(diagnosis)
        return dtos.Diagnosis.from_orm(updated_diagnosis)

    @register_method
    @validate_arguments
    def delete(self, diagnosis_id: int) -> dtos.Diagnosis:
        diagnosis = self.diagnoses_repo.fetch_by_id(diagnosis_id)

        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)

        removed_diagnosis: entities.Diagnosis = self.diagnoses_repo.remove(diagnosis)
        return dtos.Diagnosis.from_orm(removed_diagnosis)
