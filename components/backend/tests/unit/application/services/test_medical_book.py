from unittest.mock import Mock, call

import pytest

from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def med_books_repo() -> Mock:
    return Mock(interfaces.MedicalBooksRepo)


@pytest.fixture(scope='function')
def patients_repo() -> Mock:
    return Mock(interfaces.PatientsRepo)


@pytest.fixture(scope='function')
def diagnoses_repo() -> Mock:
    return Mock(interfaces.DiagnosesRepo)


@pytest.fixture(scope='function')
def symptoms_repo() -> Mock:
    return Mock(interfaces.SymptomsRepo)


@pytest.fixture(scope='function')
def reviews_repo() -> Mock:
    return Mock(interfaces.ItemReviewsRepo)


@pytest.fixture(scope='function')
def service(med_books_repo,
            patients_repo,
            diagnoses_repo,
            symptoms_repo,
            reviews_repo
            ) -> services.MedicalBook:
    return services.MedicalBook(medical_books_repo=med_books_repo,
                                patients_repo=patients_repo,
                                diagnoses_repo=diagnoses_repo,
                                symptoms_repo=symptoms_repo,
                                reviews_repo=reviews_repo)


# patient_id, is_helped, diagnosis_id, symptom_ids, match_all_symptoms, item_ids,
# repo_method
filter_params_combinations: list[tuple] = [
    (1, True, 1, [1, 2], True, None,
     'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'),
    (1, False, 1, [1, 2], True, None,
     'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'),
    (1, True, 1, [1, 2], False, None,
     'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'),
    (1, False, 1, [1, 2], False, None,
     'fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms'),

    (1, True, 1, [1, 2], None, None,
     'fetch_by_patient_helped_status_diagnosis_and_symptoms'),
    (1, False, 1, [1, 2], None, None,
     'fetch_by_patient_helped_status_diagnosis_and_symptoms'),

    (1, True, 1, None, None, None,
     'fetch_by_patient_helped_status_and_diagnosis'),
    (1, False, 1, None, None, None,
     'fetch_by_patient_helped_status_and_diagnosis'),

    (1, True, None, [1, 2], True, None,
     'fetch_by_patient_helped_status_with_matching_all_symptoms'),
    (1, True, None, [1, 2], False, None,
     'fetch_by_patient_helped_status_with_matching_all_symptoms'),
    (1, False, None, [1, 2], True, None,
     'fetch_by_patient_helped_status_with_matching_all_symptoms'),
    (1, False, None, [1, 2], False, None,
     'fetch_by_patient_helped_status_with_matching_all_symptoms'),

    (1, True, None, [1, 2], None, None,
     'fetch_by_patient_helped_status_and_symptoms'),
    (1, False, None, [1, 2], None, None,
     'fetch_by_patient_helped_status_and_symptoms'),

    (1, True, None, None, None, None, 'fetch_by_patient_and_helped_status'),
    (1, False, None, None, None, None, 'fetch_by_patient_and_helped_status'),

    (1, None, 1, [1, 2], True, None,
     'fetch_by_patient_diagnosis_with_matching_all_symptoms'),
    (1, None, 1, [1, 2], False, None,
     'fetch_by_patient_diagnosis_with_matching_all_symptoms'),

    (1, None, 1, [1, 2], None, None,
     'fetch_by_patient_diagnosis_and_symptoms'),

    (1, None, 1, None, None, None,
     'fetch_by_patient_and_diagnosis'),

    (1, None, None, [1, 2], True, None,
     'fetch_by_patient_with_matching_all_symptoms'),
    (1, None, None, [1, 2], False, None,
     'fetch_by_patient_with_matching_all_symptoms'),

    (1, None, None, [1, 2], None, None, 'fetch_by_patient_and_symptoms'),

    (1, None, None, None, None, None, 'fetch_by_patient'),

    (None, True, 1, [1, 2], True, None,
     'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'),
    (None, True, 1, [1, 2], False, None,
     'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'),
    (None, False, 1, [1, 2], True, None,
     'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'),
    (None, False, 1, [1, 2], False, None,
     'fetch_by_helped_status_diagnosis_with_matching_all_symptoms'),

    (None, True, 1, [1, 2], None, None,
     'fetch_by_helped_status_diagnosis_and_symptoms'),
    (None, False, 1, [1, 2], None, None,
     'fetch_by_helped_status_diagnosis_and_symptoms'),

    (None, True, 1, None, None, None,
     'fetch_by_helped_status_and_diagnosis'),
    (None, False, 1, None, None, None,
     'fetch_by_helped_status_and_diagnosis'),

    (None, True, None, [1, 2], True, None,
     'fetch_by_helped_status_with_matching_all_symptoms'),
    (None, True, None, [1, 2], False, None,
     'fetch_by_helped_status_with_matching_all_symptoms'),
    (None, False, None, [1, 2], True, None,
     'fetch_by_helped_status_with_matching_all_symptoms'),
    (None, False, None, [1, 2], False, None,
     'fetch_by_helped_status_with_matching_all_symptoms'),

    (None, True, None, [1, 2], None, None,
     'fetch_by_helped_status_and_symptoms'),
    (None, False, None, [1, 2], None, None,
     'fetch_by_helped_status_and_symptoms'),

    (None, True, None, None, None, None, 'fetch_by_helped_status'),
    (None, False, None, None, None, None, 'fetch_by_helped_status'),

    (None, None, 1, [1, 2], True, None,
     'fetch_by_diagnosis_with_matching_all_symptoms'),
    (None, None, 1, [1, 2], False, None,
     'fetch_by_diagnosis_with_matching_all_symptoms'),

    (None, None, 1, [1, 2], None, None, 'fetch_by_diagnosis_and_symptoms'),

    (None, None, 1, None, None, None, 'fetch_by_diagnosis'),

    (None, None, None, [1, 2], True, None, 'fetch_by_matching_all_symptoms'),
    (None, None, None, [1, 2], False, None, 'fetch_by_matching_all_symptoms'),

    (None, None, None, [1, 2], None, None, 'fetch_by_symptoms'),

    (None, None, None, None, None, None, 'fetch_all'),

    (None, None, None, None, None, [1, 2], 'fetch_by_items'),

    (1, None, None, None, None, [1, 2], 'fetch_by_patient_and_items'),

    (None, True, None, None, None, [1, 2], 'fetch_by_items_and_helped_status'),
    (None, False, None, None, None, [1, 2], 'fetch_by_items_and_helped_status'),

    (None, None, 1, None, None, [1, 2], 'fetch_by_items_and_diagnosis'),

    (None, None, None, [1, 2], None, [1, 2], 'fetch_by_items_and_symptoms'),

    (None, None, None, [1, 2], True, [1, 2],
     'fetch_by_items_with_matching_all_symptoms'),
    (None, None, None, [1, 2], False, [1, 2],
     'fetch_by_items_with_matching_all_symptoms'),

    (None, None, 1, [1, 2], True, [1, 2],
     'fetch_by_diagnosis_items_with_matching_all_symptoms'),
    (None, None, 1, [1, 2], False, [1, 2],
     'fetch_by_diagnosis_items_with_matching_all_symptoms'),

    (None, True, None, [1, 2], True, [1, 2],
     'fetch_by_helped_status_items_with_matching_all_symptoms'),
    (None, True, None, [1, 2], False, [1, 2],
     'fetch_by_helped_status_items_with_matching_all_symptoms'),
    (None, False, None, [1, 2], True, [1, 2],
     'fetch_by_helped_status_items_with_matching_all_symptoms'),
    (None, False, None, [1, 2], False, [1, 2],
     'fetch_by_helped_status_items_with_matching_all_symptoms'),

    (None, True, 1, None, None, [1, 2],
     'fetch_by_helped_status_diagnosis_and_items'),
    (None, False, 1, None, None, [1, 2],
     'fetch_by_helped_status_diagnosis_and_items'),

    (None, True, 1, [1, 2], True, [1, 2],
     'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (None, True, 1, [1, 2], False, [1, 2],
     'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (None, False, 1, [1, 2], True, [1, 2],
     'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (None, False, 1, [1, 2], False, [1, 2],
     'fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms'),

    (1, None, 1, None, None, [1, 2], 'fetch_by_patient_diagnosis_and_items'),

    (1, None, 1, [1, 2], True, [1, 2],
     'fetch_by_patient_diagnosis_items_with_matching_all_symptoms'),
    (1, None, 1, [1, 2], False, [1, 2],
     'fetch_by_patient_diagnosis_items_with_matching_all_symptoms'),

    (1, True, None, None, None, [1, 2],
     'fetch_by_patient_helped_status_and_items'),
    (1, False, None, None, None, [1, 2],
     'fetch_by_patient_helped_status_and_items'),

    (1, True, None, [1, 2], True, [1, 2],
     'fetch_by_patient_helped_status_items_with_matching_all_symptoms'),
    (1, True, None, [1, 2], False, [1, 2],
     'fetch_by_patient_helped_status_items_with_matching_all_symptoms'),
    (1, False, None, [1, 2], True, [1, 2],
     'fetch_by_patient_helped_status_items_with_matching_all_symptoms'),
    (1, False, None, [1, 2], False, [1, 2],
     'fetch_by_patient_helped_status_items_with_matching_all_symptoms'),

    (1, True, 1, None, None, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_and_items'),
    (1, False, 1, None, None, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_and_items'),

    (1, True, 1, [1, 2], True, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (1, True, 1, [1, 2], False, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (1, False, 1, [1, 2], True, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'),
    (1, False, 1, [1, 2], False, [1, 2],
     'fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms'),

]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------


class TestGetMedBook:

    def test__get_med_book(self, service, med_books_repo, patients_repo, diagnoses_repo,
                           symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        repo_output = entities.MedicalBook(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1
        )
        service_output = dtos.MedicalBook(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1
        )
        med_books_repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get_med_book(med_book_id=med_book_id)

        # Assert
        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=False, include_reviews=False
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == service_output
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    def test_medical_book_not_found(self, service, med_books_repo, patients_repo,
                                    diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get_med_book(med_book_id=med_book_id)

        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=False, include_reviews=False
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestGetMedBookWithSymptoms:

    def test__get_med_book_with_symptoms(self, service, med_books_repo, patients_repo,
                                         diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        repo_output = entities.MedicalBook(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, symptoms=[
                dtos.Symptom(id=1, name='Symptom 1'),
            ]
        )
        service_output = dtos.MedicalBookWithSymptoms(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, symptoms=[
                dtos.Symptom(id=1, name='Symptom 1'),
            ]
        )
        med_books_repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get_med_book_with_symptoms(med_book_id=med_book_id)

        # Assert
        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=True, include_reviews=False
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == service_output
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    def test_medical_book_not_found(self, service, med_books_repo, patients_repo,
                                    diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get_med_book_with_symptoms(med_book_id=med_book_id)

        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=True, include_reviews=False
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestGetMedBookWithReviews:

    def test__get_med_book_with_reviews(self, service, med_books_repo, patients_repo,
                                        diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        repo_output = entities.MedicalBook(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, item_reviews=[
                dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=7)
            ]
        )
        service_output = dtos.MedicalBookWithItemReviews(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, item_reviews=[
                dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=7)
            ]
        )
        med_books_repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get_med_book_with_reviews(med_book_id=med_book_id)

        # Assert
        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=False, include_reviews=True
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == service_output
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    def test_medical_book_not_found(self, service, med_books_repo, patients_repo,
                                    diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get_med_book_with_reviews(med_book_id=med_book_id)

        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=False, include_reviews=True
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestGetMedBookWithSymptomsAndReviews:

    def test__get_med_book_with_symptoms_and_reviews(self, service, med_books_repo,
                                                     patients_repo, diagnoses_repo,
                                                     symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        repo_output = entities.MedicalBook(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, symptoms=[dtos.Symptom(id=1, name='Symptom 1')],
            item_reviews=[
                dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=7)
            ]
        )
        service_output = dtos.MedicalBookWithSymptomsAndItemReviews(
            id=med_book_id, title_history='title', history='history', patient_id=1,
            diagnosis_id=1, symptoms=[dtos.Symptom(id=1, name='Symptom 1')],
            item_reviews=[
                dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=7)
            ]
        )
        med_books_repo.fetch_by_id.return_value = repo_output

        # Call
        result = service.get_med_book_with_symptoms_and_reviews(med_book_id=med_book_id)

        # Assert
        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=True, include_reviews=True
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert result == service_output
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    def test_medical_book_not_found(self, service, med_books_repo, patients_repo,
                                    diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.get_med_book_with_symptoms_and_reviews(med_book_id=med_book_id)

        med_books_repo.fetch_by_id.assert_called_once_with(
            med_book_id, include_symptoms=True, include_reviews=True
        )
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestFindMedBooks:

    @pytest.mark.parametrize("patient_id, is_helped, diagnosis_id, symptom_ids,"
                             " match_all_symptoms, item_ids, repo_method",
                             filter_params_combinations
                             )
    def test_find_med_books(self, patient_id, is_helped, diagnosis_id, symptom_ids,
                            match_all_symptoms, item_ids, repo_method, service,
                            med_books_repo, patients_repo, diagnoses_repo, symptoms_repo,
                            reviews_repo):
        # Setup

        filter_params = schemas.FindMedicalBooks(
            patient_id=patient_id, is_helped=is_helped, diagnosis_id=diagnosis_id,
            symptom_ids=symptom_ids, match_all_symptoms=match_all_symptoms,
            item_ids=item_ids
        )
        repo_output = [
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1)
        ]
        service_output = [
            dtos.MedicalBook(id=1, title_history='title', history='history',
                             patient_id=1, diagnosis_id=1)
        ]
        getattr(med_books_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_med_books(filter_params)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(
            filter_params, include_symptoms=False, include_reviews=False
        )
        assert result == service_output
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestFindMedBooksWithSymptoms:

    @pytest.mark.parametrize("patient_id, is_helped, diagnosis_id, symptom_ids,"
                             " match_all_symptoms, item_ids, repo_method",
                             filter_params_combinations)
    def test_find_med_books_with_symptoms(
        self, patient_id, is_helped, diagnosis_id, symptom_ids, match_all_symptoms,
        item_ids, repo_method, service, med_books_repo, patients_repo, diagnoses_repo,
        symptoms_repo, reviews_repo
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            patient_id=patient_id, is_helped=is_helped, diagnosis_id=diagnosis_id,
            symptom_ids=symptom_ids, match_all_symptoms=match_all_symptoms,
            item_ids=item_ids
        )
        repo_output = [
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1,
                                 symptoms=[entities.Symptom(id=1, name='symptom')])
        ]
        service_output = [
            dtos.MedicalBookWithSymptoms(
                id=1, title_history='title', history='history', patient_id=1,
                diagnosis_id=1, symptoms=[dtos.Symptom(id=1, name='symptom')]
            )
        ]
        getattr(med_books_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_med_books_with_symptoms(filter_params)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(
            filter_params, include_symptoms=True, include_reviews=False
        )
        assert result == service_output
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestFindMedBooksWithReviews:

    @pytest.mark.parametrize("patient_id, is_helped, diagnosis_id, symptom_ids,"
                             " match_all_symptoms, item_ids, repo_method",
                             filter_params_combinations)
    def test_find_med_books_with_reviews(
        self, patient_id, is_helped, diagnosis_id, symptom_ids, match_all_symptoms,
        item_ids, repo_method, service, med_books_repo, patients_repo, diagnoses_repo,
        symptoms_repo, reviews_repo
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            patient_id=patient_id, is_helped=is_helped, diagnosis_id=diagnosis_id,
            symptom_ids=symptom_ids, match_all_symptoms=match_all_symptoms,
            item_ids=item_ids
        )
        repo_output = [
            entities.MedicalBook(
                id=1, title_history='title', history='history', patient_id=1,
                diagnosis_id=1, item_reviews=[
                    entities.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                        item_count=7, usage_period=7)
                ]
            )
        ]
        service_output = [
            dtos.MedicalBookWithItemReviews(
                id=1, title_history='title', history='history', patient_id=1,
                diagnosis_id=1, item_reviews=[
                    dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                    item_count=7, usage_period=7)
                ]
            )
        ]
        getattr(med_books_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_med_books_with_reviews(filter_params)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(
            filter_params, include_symptoms=False, include_reviews=True
        )
        assert result == service_output
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestFindMedBooksWithSymptomsAndReviews:

    @pytest.mark.parametrize("patient_id, is_helped, diagnosis_id, symptom_ids,"
                             " match_all_symptoms, item_ids, repo_method",
                             filter_params_combinations)
    def test_find_med_books_with_symptoms_and_reviews(
        self, patient_id, is_helped, diagnosis_id, symptom_ids, match_all_symptoms,
        item_ids, repo_method, service, med_books_repo, patients_repo, diagnoses_repo,
        symptoms_repo, reviews_repo
    ):
        # Setup
        filter_params = schemas.FindMedicalBooks(
            patient_id=patient_id, is_helped=is_helped, diagnosis_id=diagnosis_id,
            symptom_ids=symptom_ids, match_all_symptoms=match_all_symptoms,
            item_ids=item_ids
        )
        repo_output = [
            entities.MedicalBook(
                id=1, title_history='title', history='history', patient_id=1,
                diagnosis_id=1, item_reviews=[
                    entities.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                        item_count=7, usage_period=7)
                ],
                symptoms=[entities.Symptom(id=1, name='symptom')]
            )
        ]
        service_output = [
            dtos.MedicalBookWithSymptomsAndItemReviews(
                id=1, title_history='title', history='history', patient_id=1,
                diagnosis_id=1, item_reviews=[
                    dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                    item_count=7, usage_period=7),
                ],
                symptoms=[dtos.Symptom(id=1, name='symptom')]
            )
        ]
        getattr(med_books_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_med_books_with_symptoms_and_reviews(filter_params)

        # Assert
        getattr(med_books_repo, repo_method).assert_called_once_with(
            filter_params, include_symptoms=True, include_reviews=True
        )
        assert result == service_output
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []


class TestAdd:
    @pytest.mark.parametrize(
        "input_dto, created_entity, repo_add_method_output, service_output", [
            (
                dtos.NewMedicalBookInfo(title_history='title', history='history',
                                        patient_id=1, diagnosis_id=1, symptom_ids=[1],
                                        item_review_ids=[2]),
                entities.MedicalBook(title_history='title', history='history',
                                     patient_id=1, diagnosis_id=1),
                entities.MedicalBook(id=1, title_history='title', history='history',
                                     patient_id=1, diagnosis_id=1,
                                     symptoms=[entities.Symptom(id=1, name='Symptom')],
                                     item_reviews=[
                                         entities.ItemReview(id=2,
                                                             item_id=1,
                                                             is_helped=True,
                                                             item_rating=8,
                                                             item_count=72000)
                                     ]
                                     ),
                dtos.MedicalBookWithSymptomsAndItemReviews(
                    id=1, title_history='title', history='history', patient_id=1,
                    diagnosis_id=1, item_reviews=[
                        dtos.ItemReview(id=2, item_id=1, is_helped=True, item_rating=8,
                                        item_count=72000, usage_period=72000)
                    ],
                    symptoms=[dtos.Symptom(id=1, name='Symptom')]
                )
            )
        ])
    def test__add_new_med_book(self, input_dto, created_entity, repo_add_method_output,
                               service_output, service, med_books_repo, patients_repo,
                               diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = repo_add_method_output.symptoms[0]
        reviews_repo.fetch_by_id.return_value = repo_add_method_output.item_reviews[0]
        med_books_repo.add.return_value = repo_add_method_output

        # Call
        result = service.add(new_med_book_info=input_dto)

        # Assert
        assert patients_repo.method_calls == [call.fetch_by_id(input_dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(input_dto.diagnosis_id)]
        assert med_books_repo.method_calls == [call.add(created_entity)]
        assert symptoms_repo.method_calls == [
            call.fetch_by_id(repo_add_method_output.symptoms[0].id)
        ]
        assert reviews_repo.method_calls == [
            call.fetch_by_id(repo_add_method_output.item_reviews[0].id)
        ]
        assert result == service_output

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=1000001, diagnosis_id=1, symptom_ids=[1],
                                item_review_ids=[2]),
    ])
    def test__patient_not_found(self, dto, service, med_books_repo, patients_repo,
                                diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == []
        assert med_books_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=1, diagnosis_id=1000001, symptom_ids=[1],
                                item_review_ids=[2]),
    ])
    def test__diagnosis_not_found(self, dto, service, med_books_repo, patients_repo,
                                  diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert med_books_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=1, diagnosis_id=1, symptom_ids=[1000001],
                                item_review_ids=[2]),
    ])
    def test__symptom_not_found(self, dto, service, med_books_repo, patients_repo,
                                diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert symptoms_repo.method_calls == [call.fetch_by_id(dto.symptom_ids[0])]
        assert reviews_repo.method_calls == []
        assert med_books_repo.method_calls == []

    @pytest.mark.parametrize("dto", [
        dtos.NewMedicalBookInfo(title_history='title', history='history',
                                patient_id=1, diagnosis_id=1, symptom_ids=[1],
                                item_review_ids=[1000001]),
    ])
    def test__item_review_not_found(self, dto, service, med_books_repo, patients_repo,
                                    diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = entities.Symptom(
            id=1, name='Symptom'
        )

        reviews_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemReviewNotFound):
            service.add(new_med_book_info=dto)

        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert symptoms_repo.method_calls == [call.fetch_by_id(dto.symptom_ids[0])]
        assert reviews_repo.method_calls == [call.fetch_by_id(dto.item_review_ids[0])]
        assert med_books_repo.method_calls == []


class TestChange:
    @pytest.mark.parametrize(
        "input_dto, repo_fetch_by_id_method_output, repo_change_method_output, "
        "service_output", [
            (
                dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                            patient_id=5, diagnosis_id=101,
                                            symptom_ids=[2], item_review_ids=[3]),
                entities.MedicalBook(id=1, title_history='title', history='history',
                                     patient_id=1, diagnosis_id=1,
                                     symptoms=[entities.Symptom(id=1, name='Symptom 1')],
                                     item_reviews=[entities.ItemReview(id=2,
                                                                       item_id=1,
                                                                       is_helped=True,
                                                                       item_rating=8,
                                                                       item_count=72000)]
                                     ),
                entities.MedicalBook(id=2, title_history='blabla', history='history',
                                     patient_id=5, diagnosis_id=101,
                                     symptoms=[entities.Symptom(id=1, name='Symptom 1'),
                                               entities.Symptom(id=2, name='Symptom 2')],
                                     item_reviews=[entities.ItemReview(id=2,
                                                                       item_id=1,
                                                                       is_helped=True,
                                                                       item_rating=8,
                                                                       item_count=72000),
                                                   entities.ItemReview(id=3,
                                                                       item_id=1,
                                                                       is_helped=False,
                                                                       item_rating=4,
                                                                       item_count=52000)]
                                     ),
                dtos.MedicalBookWithSymptomsAndItemReviews(
                    id=2, title_history='blabla', history='history', patient_id=5,
                    diagnosis_id=101,
                    symptoms=[dtos.Symptom(id=1, name='Symptom 1'),
                              dtos.Symptom(id=2, name='Symptom 2')],
                    item_reviews=[
                        dtos.ItemReview(id=2, item_id=1, is_helped=True, item_rating=8,
                                        item_count=72000),
                        dtos.ItemReview(id=3, item_id=1, is_helped=False, item_rating=4,
                                        item_count=52000)
                    ]
                )

            )
        ])
    def test__change_med_book(self, input_dto, repo_fetch_by_id_method_output,
                              repo_change_method_output, service_output, service,
                              med_books_repo, patients_repo, diagnoses_repo,
                              symptoms_repo, reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = repo_fetch_by_id_method_output
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=5, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=101, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = repo_change_method_output.symptoms[0]
        reviews_repo.fetch_by_id.return_value = repo_change_method_output.item_reviews[0]

        # Call
        result = service.change(new_med_book_info=input_dto)

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_id(input_dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == [call.fetch_by_id(input_dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(input_dto.diagnosis_id)]
        assert symptoms_repo.method_calls == [
            call.fetch_by_id(input_dto.symptom_ids[0])
        ]
        assert reviews_repo.method_calls == [
            call.fetch_by_id(input_dto.item_review_ids[0])
        ]
        assert result == service_output

    @pytest.mark.parametrize("dto", [
        dtos.UpdatedMedicalBookInfo(id=100001, title_history='blabla',
                                    patient_id=5, diagnosis_id=101,
                                    symptom_ids=[2], item_review_ids=[3]),
    ])
    def test__med_book_not_found(self, dto, service, med_books_repo,
                                 patients_repo, diagnoses_repo, symptoms_repo,
                                 reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1,
                                 symptoms=[entities.Symptom(id=1, name='Symptom')],
                                 item_reviews=[entities.ItemReview(id=2,
                                                                   item_id=1,
                                                                   is_helped=True,
                                                                   item_rating=8,
                                                                   item_count=72000)]),
            dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                        patient_id=100001, diagnosis_id=101,
                                        symptom_ids=[2], item_review_ids=[3]),
        )
    ])
    def test__patient_not_found(self, existing_entity, dto, service, med_books_repo,
                                patients_repo, diagnoses_repo, symptoms_repo,
                                reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.PatientNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1,
                                 symptoms=[entities.Symptom(id=1, name='Symptom')],
                                 item_reviews=[entities.ItemReview(id=2,
                                                                   item_id=1,
                                                                   is_helped=True,
                                                                   item_rating=8,
                                                                   item_count=72000)]),
            dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                        patient_id=1, diagnosis_id=100001,
                                        symptom_ids=[2], item_review_ids=[3]),
        )
    ])
    def test__diagnosis_not_found(self, existing_entity, dto, service, med_books_repo,
                                  patients_repo, diagnoses_repo, symptoms_repo,
                                  reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.DiagnosisNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1,
                                 symptoms=[entities.Symptom(id=1, name='Symptom')],
                                 item_reviews=[entities.ItemReview(id=2,
                                                                   item_id=1,
                                                                   is_helped=True,
                                                                   item_rating=8,
                                                                   item_count=72000)]),
            dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                        patient_id=1, diagnosis_id=1,
                                        symptom_ids=[10001], item_review_ids=[3]),
        )
    ])
    def test__symptom_not_found(self, existing_entity, dto, service, med_books_repo,
                                patients_repo, diagnoses_repo, symptoms_repo,
                                reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.SymptomNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert symptoms_repo.method_calls == [call.fetch_by_id(dto.symptom_ids[0])]
        assert reviews_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1,
                                 symptoms=[entities.Symptom(id=1, name='Symptom')],
                                 item_reviews=[entities.ItemReview(id=2,
                                                                   item_id=1,
                                                                   is_helped=True,
                                                                   item_rating=8,
                                                                   item_count=72000)]),
            dtos.UpdatedMedicalBookInfo(id=2, title_history='blabla',
                                        patient_id=1, diagnosis_id=1,
                                        symptom_ids=[1], item_review_ids=[10001]),
        )
    ])
    def test__item_review_not_found(self, existing_entity, dto, service, med_books_repo,
                                    patients_repo, diagnoses_repo, symptoms_repo,
                                    reviews_repo):
        # Setup
        med_books_repo.fetch_by_id.return_value = existing_entity
        patients_repo.fetch_by_id.return_value = entities.Patient(
            id=1, nickname='Some', gender='male', age=18, skin_type='жирная'
        )
        diagnoses_repo.fetch_by_id.return_value = entities.Diagnosis(
            id=1, name='Diagnosis'
        )
        symptoms_repo.fetch_by_id.return_value = existing_entity.symptoms[0]
        reviews_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemReviewNotFound):
            service.change(new_med_book_info=dto)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(dto.id, include_symptoms=True, include_reviews=True)
        ]
        assert patients_repo.method_calls == [call.fetch_by_id(dto.patient_id)]
        assert diagnoses_repo.method_calls == [call.fetch_by_id(dto.diagnosis_id)]
        assert symptoms_repo.method_calls == [call.fetch_by_id(dto.symptom_ids[0])]
        assert reviews_repo.method_calls == [call.fetch_by_id(dto.item_review_ids[0])]


class TestDelete:
    @pytest.mark.parametrize(
        "repo_fetch_by_id_output, repo_remove_output, service_output", [
            (
                entities.MedicalBook(id=1, title_history='title', history='history',
                                     patient_id=1, diagnosis_id=1),
                entities.MedicalBook(id=1, title_history='title', history='history',
                                     patient_id=1, diagnosis_id=1),
                dtos.MedicalBook(id=1, title_history='title', history='history',
                                 patient_id=1, diagnosis_id=1),
            )
        ]
    )
    def test__delete_med_book(self, repo_fetch_by_id_output, repo_remove_output,
                              service_output, service, med_books_repo, patients_repo,
                              diagnoses_repo, symptoms_repo, reviews_repo):
        # Setup
        med_book_id = 1
        med_books_repo.fetch_by_id.return_value = repo_fetch_by_id_output
        med_books_repo.remove.return_value = service_output

        # Call
        result = service.delete(med_book_id=med_book_id)

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_id(repo_fetch_by_id_output.id,
                             include_symptoms=False,
                             include_reviews=False),
            call.remove(repo_fetch_by_id_output)
        ]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
        assert symptoms_repo.method_calls == []
        assert reviews_repo.method_calls == []
        assert result == service_output

    def test__medical_book_not_found(self, service, med_books_repo, patients_repo,
                                     diagnoses_repo):
        # Setup
        med_book_id = 10001
        med_books_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.MedicalBookNotFound):
            service.delete(med_book_id=med_book_id)

        assert med_books_repo.method_calls == [
            call.fetch_by_id(med_book_id, include_symptoms=False, include_reviews=False)
        ]
        assert patients_repo.method_calls == []
        assert diagnoses_repo.method_calls == []
