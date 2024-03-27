from typing import Sequence

from pydantic import validate_arguments

from simple_medication_selection.application import (
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
    def get(self, symptom_id: int) -> entities.Symptom:
        symptom = self.symptoms_repo.fetch_by_id(symptom_id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        return symptom

    @register_method
    @validate_arguments
    def find_symptoms(self,
                      filter_params: schemas.FindSymptoms
                      ) -> Sequence[entities.Symptom | None]:
        if filter_params.keywords:
            return self.symptoms_repo.search_by_name(filter_params)

        return self.symptoms_repo.fetch_all(filter_params)

    @register_method
    @validate_arguments
    def create(self, new_symptom_info: dtos.NewSymptomInfo) -> entities.Symptom:
        symptom: entities.Symptom = (
            self.symptoms_repo.fetch_by_name(new_symptom_info.name)
        )

        if symptom:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        new_symptom: entities.Symptom = new_symptom_info.create_obj(entities.Symptom)
        return self.symptoms_repo.add(new_symptom)

    @register_method
    @validate_arguments
    def change(self, new_symptom_info: dtos.Symptom) -> entities.Symptom:
        symptom: entities.Symptom = self.symptoms_repo.fetch_by_id(new_symptom_info.id)
        if not symptom:
            raise errors.SymptomNotFound(id=new_symptom_info.id)

        if new_symptom_info.name == symptom.name:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        return new_symptom_info.populate_obj(symptom)

    @register_method
    @validate_arguments
    def delete(self, symptom_id: int) -> entities.Symptom:
        symptom = self.symptoms_repo.fetch_by_id(symptom_id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        return self.symptoms_repo.remove(symptom)
