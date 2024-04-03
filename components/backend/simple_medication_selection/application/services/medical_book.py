from collections import namedtuple
from typing import Sequence, Callable

from pydantic import validate_arguments

from simple_medication_selection.application import (
    dtos, entities, interfaces, errors, schemas
)
from simple_medication_selection.application import utils

decorated_function_registry = utils.DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class _MedBookSearchStrategySelector:
    """
    Предназначен для выбора стратегии по поиску медицинских карт пациента.
    Паттерн стратегия.
    """

    def __init__(self, med_books_repo: interfaces.MedicalBooksRepo) -> None:
        self.med_books_repo = med_books_repo
        self.StrategyKey = namedtuple(
            'StrategyKey',
            ['patient_id', 'is_helped', 'diagnosis_id', 'symptom_ids',
             'match_all_symptoms']
        )
        self.strategies: dict[namedtuple, Callable] = {
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_helped_status_diagnosis_and_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_helped_status_and_diagnosis
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_helped_status_and_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_and_helped_status
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self.med_books_repo.fetch_by_patient_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_diagnosis_and_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_and_diagnosis
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self.med_books_repo.fetch_by_patient_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient_and_symptoms
            ),
            self.StrategyKey(patient_id=True,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_patient
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self
                .med_books_repo
                .fetch_by_helped_status_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_helped_status_diagnosis_and_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=True,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_helped_status_and_diagnosis
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self.med_books_repo.fetch_by_helped_status_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_helped_status_and_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=True,
                             diagnosis_id=False,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_helped_status
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self.med_books_repo.fetch_by_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_diagnosis_and_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=True,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_diagnosis
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=True): (
                self.med_books_repo.fetch_by_matching_all_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=True,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_by_symptoms
            ),
            self.StrategyKey(patient_id=False,
                             is_helped=False,
                             diagnosis_id=False,
                             symptom_ids=False,
                             match_all_symptoms=False): (
                self.med_books_repo.fetch_all
            )
        }

    def _build_key(
        self,
        filter_params: schemas.FindMedicalBooks | schemas.FindPatientMedicalBooks
    ) -> namedtuple:

        if isinstance(filter_params, schemas.FindPatientMedicalBooks):
            patient_id = True if filter_params.patient_id is not None else False
        else:
            patient_id = None

        return self.StrategyKey(
            patient_id=True if patient_id is not None else False,
            is_helped=True if filter_params.is_helped is not None else False,
            diagnosis_id=True if filter_params.diagnosis_id is not None else False,
            symptom_ids=True if filter_params.symptom_ids is not None else False,
            match_all_symptoms=(True
                                if filter_params.match_all_symptoms is not None
                                else False)
        )

    def get_method(
        self,
        filter_params: schemas.FindMedicalBooks | schemas.FindPatientMedicalBooks
    ) -> Callable:

        key: namedtuple = self._build_key(filter_params)
        return self.strategies.get(key)


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
    @validate_arguments
    def get_med_book(self,
                     med_book_id: int,
                     include_symptoms: bool = False,
                     include_reviews: bool = False
                     ) -> (entities.MedicalBook |
                           dtos.MedicalBook |
                           dtos.MedicalBookWithSymptoms |
                           dtos.MedicalBookWithItemReviews):

        StrategyKey = namedtuple('StrategyKey',
                                 ['include_symptoms', 'include_reviews'])

        strategies: dict[namedtuple, Callable] = {
            StrategyKey(include_symptoms=True, include_reviews=True): (
                self.med_books_repo.fetch_by_id_with_symptoms_and_reviews
            ),
            StrategyKey(include_symptoms=True, include_reviews=False): (
                self.med_books_repo.fetch_by_id_with_symptoms
            ),
            StrategyKey(include_symptoms=False, include_reviews=True): (
                self.med_books_repo.fetch_by_id_with_reviews
            ),
            StrategyKey(include_symptoms=False, include_reviews=False): (
                self.med_books_repo.fetch_by_id
            )
        }
        medical_book: (entities.MedicalBook |
                       dtos.MedicalBook |
                       dtos.MedicalBookWithSymptoms |
                       dtos.MedicalBookWithItemReviews) = (
            strategies.get(StrategyKey(include_symptoms, include_reviews))(med_book_id)
        )

        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return medical_book

    @register_method
    @validate_arguments
    def find_med_books(
        self,
        filter_params: schemas.FindMedicalBooks | schemas.FindPatientMedicalBooks,
    ) -> (Sequence[entities.MedicalBook | None] |
          list[dtos.MedicalBook |
               dtos.MedicalBookWithSymptoms |
               dtos.MedicalBookWithItemReviews |
               None]):

        strategy_selector = _MedBookSearchStrategySelector(self.med_books_repo)
        repo_method = strategy_selector.get_method(filter_params)

        return repo_method(filter_params)

    @register_method
    @validate_arguments
    def add(self,
            new_med_book_info: dtos.NewMedicalBookInfo
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
    @validate_arguments
    def change(self,
               new_med_book_info: dtos.UpdatedMedicalBookInfo
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
