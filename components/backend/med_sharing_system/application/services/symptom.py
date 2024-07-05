from typing import Sequence

from pydantic import validate_arguments

from med_sharing_system.application import (
    dtos, entities, interfaces, errors, schemas
)
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Symptom:
    def __init__(self, symptoms_repo: interfaces.SymptomsRepo):
        self.symptoms_repo = symptoms_repo

    @register_method
    @validate_arguments
    def get(self, symptom_id: int) -> dtos.Symptom:
        symptom = self.symptoms_repo.fetch_by_id(symptom_id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        return dtos.Symptom.from_orm(symptom)

    @register_method
    @validate_arguments
    def find_symptoms(self,
                      filter_params: schemas.FindSymptoms
                      ) -> list[dtos.Symptom | None]:
        if filter_params.keywords:
            found_symptoms: Sequence[entities.Symptom | None] = (
                self.symptoms_repo.search_by_name(filter_params)
            )
        else:
            found_symptoms: Sequence[entities.Symptom | None] = (
                self.symptoms_repo.fetch_all(filter_params)
            )

        return [dtos.Symptom.from_orm(symptom) for symptom in found_symptoms]

    @register_method
    @validate_arguments
    def add(self, new_symptom_info: dtos.NewSymptomInfo) -> dtos.Symptom:
        symptom: entities.Symptom = (
            self.symptoms_repo.fetch_by_name(new_symptom_info.name)
        )
        if symptom:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        new_symptom: entities.Symptom = new_symptom_info.create_obj(entities.Symptom)
        added_symptom: entities.Symptom = self.symptoms_repo.add(new_symptom)
        return dtos.Symptom.from_orm(added_symptom)

    @register_method
    @validate_arguments
    def change(self, new_symptom_info: dtos.Symptom) -> dtos.Symptom:
        symptom: entities.Symptom = self.symptoms_repo.fetch_by_id(new_symptom_info.id)
        if not symptom:
            raise errors.SymptomNotFound(id=new_symptom_info.id)

        symptom_with_same_name = self.symptoms_repo.fetch_by_name(new_symptom_info.name)
        if symptom_with_same_name and symptom_with_same_name.id != symptom.id:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        updated_symptom: entities.Symptom = new_symptom_info.populate_obj(symptom)
        return dtos.Symptom.from_orm(updated_symptom)

    @register_method
    @validate_arguments
    def delete(self, symptom_id: int) -> dtos.Symptom:
        symptom: entities.Symptom = self.symptoms_repo.fetch_by_id(symptom_id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        removed_symptom: entities.Symptom = self.symptoms_repo.remove(symptom)
        return dtos.Symptom.from_orm(removed_symptom)
