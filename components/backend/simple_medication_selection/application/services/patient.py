from collections import namedtuple
from typing import Callable, Sequence

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Patient:
    def __init__(self, patients_repo: interfaces.PatientsRepo):
        self.patients_repo = patients_repo
        self.search_strategy_selector = _PatientStrategySelector(patients_repo)

    @register_method
    @validate_arguments
    def get(self, patient_id: int) -> entities.Patient:
        patient = self.patients_repo.fetch_by_id(patient_id)

        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        return patient

    def find(self, filter_params: schemas.FindPatients) -> Sequence[entities.Patient]:
        repo_method: Callable = self.search_strategy_selector.get_method(filter_params)

        return repo_method(filter_params)

    @register_method
    @validate_arguments
    def create(self, new_patient_info: dtos.PatientCreateSchema) -> entities.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
        )
        if patient:
            raise errors.PatientAlreadyExists(nickname=new_patient_info.nickname)

        new_patient: entities.Patient = new_patient_info.create_obj(entities.Patient)

        return self.patients_repo.add(new_patient)

    @register_method
    @validate_arguments
    def change(self, new_patient_info: dtos.PatientUpdateSchema) -> entities.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
        )
        if not patient:
            raise errors.PatientNotFound(id=new_patient_info.id)

        if patient.nickname == new_patient_info.nickname:
            raise errors.PatientAlreadyExists(nickname=new_patient_info.nickname)

        return new_patient_info.populate_obj(patient)

    @register_method
    @validate_arguments
    def delete(self, patient_id: int) -> entities.Patient:
        patient = self.patients_repo.fetch_by_id(patient_id)

        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        return self.patients_repo.remove(patient)


class _PatientStrategySelector:
    def __init__(self, patients_repo: interfaces.PatientsRepo):
        self.patients_repo = patients_repo
        self.StrategyKey = namedtuple(
            'StrategyKey',
            ['gender', 'age', 'skin_type']
        )
        self.strategies: dict[namedtuple, Callable] = {
            self.StrategyKey(False, False, False): (
                self.patients_repo.fetch_all
            ),
            self.StrategyKey(True, False, False): (
                self.patients_repo.fetch_by_gender
            ),
            self.StrategyKey(False, True, False): (
                self.patients_repo.fetch_by_age
            ),
            self.StrategyKey(False, False, True): (
                self.patients_repo.fetch_by_skin_type
            ),
            self.StrategyKey(True, True, False): (
                self.patients_repo.fetch_by_gender_and_age
            ),
            self.StrategyKey(True, False, True): (
                self.patients_repo.fetch_by_gender_and_skin_type
            ),
            self.StrategyKey(False, True, True): (
                self.patients_repo.fetch_by_age_and_skin_type
            ),
            self.StrategyKey(True, True, True): (
                self.patients_repo.fetch_by_gender_age_and_skin_type
            )
        }

    def _build_key(self, filter_params: schemas.FindPatients) -> namedtuple:

        return self.StrategyKey(
            gender=True if filter_params.gender is not None else False,
            age=any((filter_params.age_from is not None,
                     filter_params.age_to is not None)),
            skin_type=True if filter_params.skin_type is not None else False
        )

    def get_method(self, filter_params: schemas.FindPatients) -> Callable:
        key: namedtuple = self._build_key(filter_params)
        return self.strategies[key]
