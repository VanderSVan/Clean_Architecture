import uuid
from collections import namedtuple
from typing import Callable, Sequence

from pydantic import validate_arguments

from med_sharing_system.application import (
    dtos, entities, interfaces, errors, schemas
)
from med_sharing_system.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class Patient:
    def __init__(self,
                 patients_repo: interfaces.PatientsRepo,
                 medical_books_repo: interfaces.MedicalBooksRepo):
        self.patients_repo = patients_repo
        self.medical_books_repo = medical_books_repo
        self.search_strategy_selector = _PatientStrategySelector(patients_repo)

    @register_method
    @validate_arguments
    def get(self, patient_id: int) -> dtos.Patient:
        patient: entities.Patient = self.patients_repo.fetch_by_id(patient_id)

        if not patient:
            raise errors.PatientNotFound(id=patient_id)

        return dtos.Patient.from_orm(patient)

    def find(self, filter_params: schemas.FindPatients) -> list[dtos.Patient | None]:
        repo_method: Callable = self.search_strategy_selector.get_method(filter_params)

        patients: Sequence[entities.Patient | None] = repo_method(filter_params)

        return [dtos.Patient.from_orm(patient) for patient in patients]

    @register_method
    @validate_arguments
    def add(self, new_patient_info: dtos.NewPatientInfo) -> dtos.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
        )
        if patient:
            raise errors.PatientAlreadyExists(nickname=new_patient_info.nickname)

        new_patient: entities.Patient = new_patient_info.create_obj(entities.Patient)
        added_patient: entities.Patient = self.patients_repo.add(new_patient)
        return dtos.Patient.from_orm(added_patient)

    @register_method
    @validate_arguments
    def change(self, new_patient_info: dtos.UpdatedPatientInfo) -> dtos.Patient:
        patient: entities.Patient = (
            self.patients_repo.fetch_by_id(new_patient_info.id)
        )
        if not patient:
            raise errors.PatientNotFound(id=new_patient_info.id)

        if new_patient_info.nickname:
            patient_with_same_nickname: entities.Patient = (
                self.patients_repo.fetch_by_nickname(new_patient_info.nickname)
            )
            if (
                patient_with_same_nickname and
                patient_with_same_nickname.id != new_patient_info.id
            ):
                raise errors.PatientAlreadyExists(nickname=new_patient_info.nickname)

        updated_patient: entities.Patient = new_patient_info.populate_obj(patient)
        return dtos.Patient.from_orm(updated_patient)

    @register_method
    @validate_arguments
    def delete(self, patient_id: int) -> dtos.Patient:
        # Получаем удаляемого пациента
        patient_to_delete: entities.Patient = self.patients_repo.fetch_by_id(patient_id)

        if not patient_to_delete:
            raise errors.PatientNotFound(id=patient_id)

        # Находим все MedicalBook, связанные с удаляемым пациентом
        medical_books_filter_params = schemas.FindMedicalBooks(patient_id=patient_id)
        medical_books_to_move: Sequence[entities.MedicalBook] = (
            self.medical_books_repo.fetch_by_patient(medical_books_filter_params,
                                                     include_symptoms=False,
                                                     include_reviews=False)
        )

        # Создаем нового пациента с ником Anonymous-{} и
        # передаем ему нечувствительные данные
        new_patient_nickname: str = f"Anonymous-{uuid.uuid4()}"
        patient_to_create: entities.Patient = (
            self.patients_repo.fetch_by_nickname(new_patient_nickname)
        )
        if patient_to_create:
            raise errors.PatientCannotBeDeleted(nickname=patient_to_delete.nickname)

        new_patient_info = dtos.NewPatientInfo(
            nickname=new_patient_nickname, gender=patient_to_delete.gender,
            age=patient_to_delete.age, skin_type=patient_to_delete.skin_type
        )
        new_patient: entities.Patient = new_patient_info.create_obj(entities.Patient)
        added_patient: entities.Patient = self.patients_repo.add(new_patient)

        # Обновляем ссылку на пациента во всех найденных MedicalBook
        for medical_book in medical_books_to_move:
            medical_book.patient_id = added_patient.id

        removed_patient: entities.Patient = self.patients_repo.remove(patient_to_delete)
        return dtos.Patient.from_orm(removed_patient)


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
