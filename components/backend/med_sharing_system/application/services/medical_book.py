from collections import namedtuple
from functools import singledispatchmethod
from typing import Callable, Sequence

from pydantic import validate_arguments

from med_sharing_system.application import (
    dtos, entities, interfaces, errors, schemas
)
from med_sharing_system.application import utils

decorated_function_registry = utils.DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class MedicalBook:
    def __init__(self,
                 medical_books_repo: interfaces.MedicalBooksRepo,
                 patients_repo: interfaces.PatientsRepo,
                 diagnoses_repo: interfaces.DiagnosesRepo,
                 symptoms_repo: interfaces.SymptomsRepo,
                 reviews_repo: interfaces.ItemReviewsRepo
                 ) -> None:
        self.med_books_repo = medical_books_repo
        self.patients_repo = patients_repo
        self.diagnoses_repo = diagnoses_repo
        self.symptoms_repo = symptoms_repo
        self.reviews_repo = reviews_repo
        self._search_strategy_selector = (
            _MedBookSearchStrategySelector(medical_books_repo)
        )
        self._entity_checker = _EntityExistsChecker()

    @register_method
    @validate_arguments
    def get_med_book(self, med_book_id: int) -> dtos.MedicalBook:

        medical_book: entities.MedicalBook = self.med_books_repo.fetch_by_id(
            med_book_id, include_symptoms=False, include_reviews=False
        )

        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return dtos.MedicalBook.from_orm(medical_book)

    @register_method
    @validate_arguments
    def get_med_book_with_symptoms(self,
                                   med_book_id: int
                                   ) -> dtos.MedicalBookWithSymptoms:

        medical_book: entities.MedicalBook = self.med_books_repo.fetch_by_id(
            med_book_id, include_symptoms=True, include_reviews=False
        )

        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return dtos.MedicalBookWithSymptoms.from_orm(medical_book)

    @register_method
    @validate_arguments
    def get_med_book_with_reviews(self,
                                  med_book_id: int
                                  ) -> dtos.MedicalBookWithItemReviews:

        medical_book: entities.MedicalBook = self.med_books_repo.fetch_by_id(
            med_book_id, include_symptoms=False, include_reviews=True
        )

        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return dtos.MedicalBookWithItemReviews.from_orm(medical_book)

    @register_method
    @validate_arguments
    def get_med_book_with_symptoms_and_reviews(
        self,
        med_book_id: int
    ) -> dtos.MedicalBookWithSymptomsAndItemReviews:

        medical_book: entities.MedicalBook = self.med_books_repo.fetch_by_id(
            med_book_id, include_symptoms=True, include_reviews=True
        )

        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        return dtos.MedicalBookWithSymptomsAndItemReviews.from_orm(medical_book)

    @register_method
    @validate_arguments
    def find_med_books(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBook | None]:

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        med_books: Sequence[entities.MedicalBook | None] = (
            repo_method(filter_params, include_symptoms=False, include_reviews=False)
        )

        return [dtos.MedicalBook.from_orm(med_book) for med_book in med_books]

    @register_method
    @validate_arguments
    def find_med_books_with_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        med_books: Sequence[entities.MedicalBook | None] = (
            repo_method(filter_params, include_symptoms=True, include_reviews=False)
        )

        return [dtos.MedicalBookWithSymptoms.from_orm(med_book) for med_book in med_books]

    @register_method
    @validate_arguments
    def find_med_books_with_reviews(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBookWithItemReviews | None]:

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        med_books: Sequence[entities.MedicalBook | None] = (
            repo_method(filter_params, include_symptoms=False, include_reviews=True)
        )

        return [dtos.MedicalBookWithItemReviews.from_orm(med_book)
                for med_book in med_books]

    @register_method
    @validate_arguments
    def find_med_books_with_symptoms_and_reviews(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptomsAndItemReviews | None]:

        repo_method: Callable = self._search_strategy_selector.get_method(filter_params)
        med_books: Sequence[entities.MedicalBook | None] = (
            repo_method(filter_params, include_symptoms=True, include_reviews=True)
        )

        return [dtos.MedicalBookWithSymptomsAndItemReviews.from_orm(med_book)
                for med_book in med_books]

    @register_method
    @validate_arguments
    def add(self,
            new_med_book_info: dtos.NewMedicalBookInfo
            ) -> dtos.MedicalBookWithSymptomsAndItemReviews:

        # Проверки
        self._entity_checker.check_and_return(
            self.patients_repo, new_med_book_info.patient_id
        )
        self._entity_checker.check_and_return(
            self.diagnoses_repo, new_med_book_info.diagnosis_id
        )

        # Создание новой сущности без симптомов и отзывов
        medical_book: entities.MedicalBook = new_med_book_info.create_obj(
            entities.MedicalBook, exclude={'symptom_ids', 'item_review_ids'}
        )
        schema: dict = new_med_book_info.schema()['properties']

        # Добавление симптомов и отзывов
        if schema.get('symptom_ids'):
            symptoms: list[entities.Symptom] = [
                self._entity_checker.check_and_return(self.symptoms_repo, symptom_id)
                for symptom_id in new_med_book_info.symptom_ids
            ]
            medical_book.symptoms = symptoms

        if schema.get('item_review_ids'):
            reviews: list[entities.ItemReview] = [
                self._entity_checker.check_and_return(self.reviews_repo, review_id)
                for review_id in new_med_book_info.item_review_ids
            ]
            medical_book.item_reviews = reviews

        added_medical_book = self.med_books_repo.add(medical_book)
        return dtos.MedicalBookWithSymptomsAndItemReviews.from_orm(added_medical_book)

    @register_method
    @validate_arguments
    def change(self, new_med_book_info) -> dtos.MedicalBookWithSymptomsAndItemReviews:

        # Проверки
        found_medical_book: entities.MedicalBook = (
            self._entity_checker.check_and_return(self.med_books_repo,
                                                  new_med_book_info.id)
        )
        self._entity_checker.check_and_return(self.patients_repo,
                                              new_med_book_info.patient_id)
        self._entity_checker.check_and_return(self.diagnoses_repo,
                                              new_med_book_info.diagnosis_id)

        # Изменение существующей информации
        change_method = _ChangeMethodHandler(
            self._entity_checker, self.symptoms_repo, self.reviews_repo
        )
        updated_med_book: entities.MedicalBook = (
            change_method.execute(new_med_book_info, found_medical_book)
        )

        return dtos.MedicalBookWithSymptomsAndItemReviews.from_orm(updated_med_book)

    @register_method
    @validate_arguments
    def delete(self, med_book_id: int) -> dtos.MedicalBook:

        medical_book: entities.MedicalBook = (
            self.med_books_repo.fetch_by_id(med_book_id,
                                            include_symptoms=False,
                                            include_reviews=False)
        )
        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)

        removed_med_book = self.med_books_repo.remove(medical_book)
        return dtos.MedicalBook.from_orm(removed_med_book)


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
             'match_all_symptoms', 'item_ids']
        )
        self.strategies: dict[namedtuple, Callable] = {
            self.StrategyKey(True, True, True, True, True, False): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(True, True, True, True, False, False): (
                self.med_books_repo.fetch_by_patient_helped_status_diagnosis_and_symptoms
            ),
            self.StrategyKey(True, True, True, False, False, False): (
                self.med_books_repo.fetch_by_patient_helped_status_and_diagnosis
            ),
            self.StrategyKey(True, True, False, True, True, False): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_with_matching_all_symptoms
            ),
            self.StrategyKey(True, True, False, True, False, False): (
                self.med_books_repo.fetch_by_patient_helped_status_and_symptoms
            ),
            self.StrategyKey(True, True, False, False, False, False): (
                self.med_books_repo.fetch_by_patient_and_helped_status
            ),
            self.StrategyKey(True, False, True, True, True, False): (
                self.med_books_repo.fetch_by_patient_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(True, False, True, True, False, False): (
                self.med_books_repo.fetch_by_patient_diagnosis_and_symptoms
            ),
            self.StrategyKey(True, False, True, False, False, False): (
                self.med_books_repo.fetch_by_patient_and_diagnosis
            ),
            self.StrategyKey(True, False, False, True, True, False): (
                self.med_books_repo.fetch_by_patient_with_matching_all_symptoms
            ),
            self.StrategyKey(True, False, False, True, False, False): (
                self.med_books_repo.fetch_by_patient_and_symptoms
            ),
            self.StrategyKey(True, False, False, False, False, False): (
                self.med_books_repo.fetch_by_patient
            ),
            self.StrategyKey(False, True, True, True, True, False): (
                self
                .med_books_repo
                .fetch_by_helped_status_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(False, True, True, True, False, False): (
                self.med_books_repo.fetch_by_helped_status_diagnosis_and_symptoms
            ),
            self.StrategyKey(False, True, True, False, False, False): (
                self.med_books_repo.fetch_by_helped_status_and_diagnosis
            ),
            self.StrategyKey(False, True, False, True, True, False): (
                self.med_books_repo.fetch_by_helped_status_with_matching_all_symptoms
            ),
            self.StrategyKey(False, True, False, True, False, False): (
                self.med_books_repo.fetch_by_helped_status_and_symptoms
            ),
            self.StrategyKey(False, True, False, False, False, False): (
                self.med_books_repo.fetch_by_helped_status
            ),
            self.StrategyKey(False, False, True, True, True, False): (
                self.med_books_repo.fetch_by_diagnosis_with_matching_all_symptoms
            ),
            self.StrategyKey(False, False, True, True, False, False): (
                self.med_books_repo.fetch_by_diagnosis_and_symptoms
            ),
            self.StrategyKey(False, False, True, False, False, False): (
                self.med_books_repo.fetch_by_diagnosis
            ),
            self.StrategyKey(False, False, False, True, True, False): (
                self.med_books_repo.fetch_by_matching_all_symptoms
            ),
            self.StrategyKey(False, False, False, True, False, False): (
                self.med_books_repo.fetch_by_symptoms
            ),
            self.StrategyKey(False, False, False, False, False, False): (
                self.med_books_repo.fetch_all
            ),
            self.StrategyKey(False, False, False, False, False, True): (
                self.med_books_repo.fetch_by_items
            ),
            self.StrategyKey(True, False, False, False, False, True): (
                self.med_books_repo.fetch_by_patient_and_items
            ),
            self.StrategyKey(False, True, False, False, False, True): (
                self.med_books_repo.fetch_by_items_and_helped_status
            ),
            self.StrategyKey(False, False, True, False, False, True): (
                self.med_books_repo.fetch_by_items_and_diagnosis
            ),
            self.StrategyKey(False, False, False, True, False, True): (
                self.med_books_repo.fetch_by_items_and_symptoms
            ),
            self.StrategyKey(False, False, False, True, True, True): (
                self.med_books_repo.fetch_by_items_with_matching_all_symptoms
            ),
            self.StrategyKey(False, False, True, True, True, True): (
                self.med_books_repo.fetch_by_diagnosis_items_with_matching_all_symptoms
            ),
            self.StrategyKey(False, True, False, True, True, True): (
                self
                .med_books_repo
                .fetch_by_helped_status_items_with_matching_all_symptoms
            ),
            self.StrategyKey(False, True, True, False, False, True): (
                self.med_books_repo.fetch_by_helped_status_diagnosis_and_items
            ),
            self.StrategyKey(False, True, True, True, True, True): (
                self
                .med_books_repo
                .fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms
            ),
            self.StrategyKey(True, False, True, False, False, True): (
                self.med_books_repo.fetch_by_patient_diagnosis_and_items
            ),
            self.StrategyKey(True, False, True, True, True, True): (
                self
                .med_books_repo
                .fetch_by_patient_diagnosis_items_with_matching_all_symptoms
            ),
            self.StrategyKey(True, True, False, False, False, True): (
                self.med_books_repo.fetch_by_patient_helped_status_and_items
            ),
            self.StrategyKey(True, True, False, True, True, True): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_items_with_matching_all_symptoms
            ),
            self.StrategyKey(True, True, True, False, False, True): (
                self.med_books_repo.fetch_by_patient_helped_status_diagnosis_and_items
            ),
            self.StrategyKey(True, True, True, True, True, True): (
                self
                .med_books_repo
                .fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms
            )
        }

    def _build_key(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> namedtuple:
        return self.StrategyKey(
            patient_id=True if filter_params.patient_id is not None else False,
            is_helped=True if filter_params.is_helped is not None else False,
            diagnosis_id=True if filter_params.diagnosis_id is not None else False,
            symptom_ids=True if filter_params.symptom_ids is not None else False,
            match_all_symptoms=(True
                                if filter_params.match_all_symptoms is not None
                                else False),
            item_ids=True if filter_params.item_ids is not None else False
        )

    def get_method(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Callable:
        key: namedtuple = self._build_key(filter_params)
        return self.strategies.get(key)


class _EntityExistsChecker:

    @singledispatchmethod
    def check_and_return(self, repo, entity_id):
        raise NotImplementedError(f"Type {type(repo)} is not supported")

    @check_and_return.register
    def _check_patient_exists(self,
                              repo: interfaces.PatientsRepo,
                              patient_id: int
                              ) -> entities.Patient | None:
        if patient_id is None:
            return None

        patient: entities.Patient = repo.fetch_by_id(patient_id)
        if not patient:
            raise errors.PatientNotFound(id=patient_id)
        return patient

    @check_and_return.register
    def _check_diagnosis_exists(self,
                                repo: interfaces.DiagnosesRepo,
                                diagnosis_id: int
                                ) -> entities.Diagnosis | None:
        if diagnosis_id is None:
            return None

        diagnosis: entities.Diagnosis = repo.fetch_by_id(diagnosis_id)
        if not diagnosis:
            raise errors.DiagnosisNotFound(id=diagnosis_id)
        return diagnosis

    @check_and_return.register
    def _check_medical_book_exists(self,
                                   repo: interfaces.MedicalBooksRepo,
                                   med_book_id: int
                                   ) -> entities.MedicalBook:
        medical_book: entities.MedicalBook = repo.fetch_by_id(med_book_id,
                                                              include_symptoms=False,
                                                              include_reviews=False)
        if not medical_book:
            raise errors.MedicalBookNotFound(id=med_book_id)
        return medical_book

    @check_and_return.register
    def _check_symptom_exists(self,
                              repo: interfaces.SymptomsRepo,
                              symptom_id: int
                              ) -> entities.Symptom | None:
        if symptom_id is None:
            return None

        symptom: entities.Symptom = repo.fetch_by_id(symptom_id)
        if not symptom:
            raise errors.SymptomNotFound(id=symptom_id)
        return symptom

    @check_and_return.register
    def _check_item_review_exists(self,
                                  repo: interfaces.ItemReviewsRepo,
                                  review_id: int
                                  ) -> entities.ItemReview | None:
        if review_id is None:
            return None

        review: entities.ItemReview = repo.fetch_by_id(review_id)
        if not review:
            raise errors.ItemReviewNotFound(id=review_id)
        return review


class _ChangeMethodHandler:
    def __init__(self,
                 entity_checker: _EntityExistsChecker,
                 symptoms_repo: interfaces.SymptomsRepo,
                 reviews_repo: interfaces.ItemReviewsRepo
                 ) -> None:
        self.entity_checker = entity_checker
        self.symptoms_repo = symptoms_repo
        self.reviews_repo = reviews_repo

    @singledispatchmethod
    def execute(self,
                new_med_book_info,
                med_book_to_change: entities.MedicalBook
                ) -> entities.MedicalBook:
        raise NotImplementedError(f"Type {type(new_med_book_info)} is not supported")

    @execute.register
    # @validate_arguments
    def _(self,
          new_med_book_info: dtos.UpdatedMedicalBookInfo,
          med_book_to_change: entities.MedicalBook
          ) -> entities.MedicalBook:

        # Замена существующей информации без симптомов и отзывов
        updated_med_book: entities.MedicalBook = new_med_book_info.populate_obj(
            med_book_to_change, exclude={'symptom_ids', 'item_review_ids'}
        )
        schema: dict = new_med_book_info.schema()['properties']

        # Замена новых симптомов
        if schema.get('symptom_ids') and new_med_book_info.symptom_ids:
            symptoms: list[entities.Symptom] = [
                self.entity_checker.check_and_return(self.symptoms_repo, symptom_id)
                for symptom_id in new_med_book_info.symptom_ids
            ]
            updated_med_book.symptoms = symptoms

        # Замена новых отзывов
        if schema.get('item_review_ids') and new_med_book_info.item_review_ids:
            reviews: list[entities.ItemReview] = [
                self.entity_checker.check_and_return(self.reviews_repo, review_id)
                for review_id in new_med_book_info.item_review_ids
            ]
            updated_med_book.item_reviews = reviews

        return updated_med_book

    @execute.register
    # @validate_arguments
    def _(self,
          new_med_book_info: dtos.MedicalBookInfoToUpdate,
          med_book_to_change: entities.MedicalBook
          ) -> entities.MedicalBook:

        # Замена существующей информации без симптомов и отзывов
        updated_med_book: entities.MedicalBook = new_med_book_info.populate_obj(
            med_book_to_change, exclude={
                'symptom_ids_to_add', 'symptom_ids_to_remove',
                'item_review_ids_to_add', 'item_review_ids_to_remove',
            }
        )
        schema: dict = new_med_book_info.schema()['properties']

        # Добавление новых симптомов
        if schema.get('symptom_ids_to_add') and new_med_book_info.symptom_ids_to_add:
            symptoms: list[entities.Symptom] = [
                self.entity_checker.check_and_return(self.symptoms_repo, symptom_id)
                for symptom_id in new_med_book_info.symptom_ids_to_add
            ]
            updated_med_book.add_symptoms(symptoms)

        # Добавление новых отзывов
        if (
            schema.get('item_review_ids_to_add') and
            new_med_book_info.item_review_ids_to_add
        ):
            reviews: list[entities.ItemReview] = [
                self.entity_checker.check_and_return(self.reviews_repo, review_id)
                for review_id in new_med_book_info.item_review_ids_to_add
            ]
            updated_med_book.add_item_reviews(reviews)

        # Удаление симптомов выборочно
        if (
            schema.get('symptom_ids_to_remove') and
            new_med_book_info.symptom_ids_to_remove
        ):
            symptoms: list[entities.Symptom] = [
                self.entity_checker.check_and_return(self.symptoms_repo, symptom_id)
                for symptom_id in new_med_book_info.symptom_ids_to_remove
            ]
            updated_med_book.remove_symptoms(symptoms)

        # Удаление отзывов выборочно
        if (
            schema.get('item_review_ids_to_remove') and
            new_med_book_info.item_review_ids_to_remove
        ):
            reviews: list[entities.ItemReview] = [
                self.entity_checker.check_and_return(self.reviews_repo, review_id)
                for review_id in new_med_book_info.item_review_ids_to_remove
            ]
            updated_med_book.remove_item_reviews(reviews)

        return updated_med_book
