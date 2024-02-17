from pydantic import validate_call

from simple_medication_selection.application import dtos, entities, interfaces, errors
from ..utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Symptom:
    def __init__(self, symptoms_repo: interfaces.SymptomsRepo):
        self.symptoms_repo = symptoms_repo

    @register_method
    @validate_call
    def get(self, symptom_id: int) -> entities.Symptom:
        symptom = self.symptoms_repo.fetch_by_id(symptom_id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)

        return symptom

    @register_method
    @validate_call
    def create(self, new_symptom_info: dtos.SymptomCreateSchema) -> None:
        symptom: entities.Symptom = (
            self.symptoms_repo.fetch_by_name(new_symptom_info.name)
        )

        if symptom:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        new_symptom: entities.Symptom = new_symptom_info.create_obj(entities.Symptom)
        self.symptoms_repo.add(new_symptom)

    @register_method
    @validate_call
    def update(self, new_symptom_info: dtos.SymptomUpdateSchema) -> None:
        symptom: entities.Symptom = self.symptoms_repo.fetch_by_id(new_symptom_info.id)
        if not symptom:
            raise errors.SymptomNotFound(id=new_symptom_info.id)

        if new_symptom_info.name == symptom.name:
            raise errors.SymptomAlreadyExists(name=new_symptom_info.name)

        new_symptom_info.populate_obj(symptom)

    @register_method
    @validate_call
    def delete(self, symptom_info: dtos.SymptomDeleteSchema) -> None:
        symptom = self.symptoms_repo.fetch_by_id(symptom_info.id)

        if not symptom:
            raise errors.SymptomNotFound(id=symptom_info.id)

        self.symptoms_repo.remove(symptom)
