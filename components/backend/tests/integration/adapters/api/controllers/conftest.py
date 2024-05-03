from unittest.mock import Mock

import pytest
from falcon import testing

from simple_medication_selection.adapters.api.app import create_app
from simple_medication_selection.application import services


@pytest.fixture(scope='function')
def item_category_service() -> Mock:
    return Mock(services.ItemCategory)


@pytest.fixture(scope='function')
def diagnosis_service() -> Mock:
    return Mock(services.Diagnosis)


@pytest.fixture(scope='function')
def patient_service() -> Mock:
    return Mock(services.Patient)


@pytest.fixture(scope='function')
def symptom_service() -> Mock:
    return Mock(services.Symptom)


@pytest.fixture(scope='function')
def item_review_service() -> Mock:
    return Mock(services.ItemReview)


@pytest.fixture(scope='function')
def catalog_service() -> Mock:
    return Mock(services.TreatmentItemCatalog)


@pytest.fixture(scope='function')
def medical_book_service() -> Mock:
    return Mock(services.MedicalBook)


@pytest.fixture(scope='function')
def client(diagnosis_service,
           patient_service,
           symptom_service,
           catalog_service,
           item_review_service,
           item_category_service,
           medical_book_service):
    app = create_app(diagnosis=diagnosis_service,
                     patient=patient_service,
                     symptom=symptom_service,
                     catalog=catalog_service,
                     item_review=item_review_service,
                     item_category=item_category_service,
                     medical_book=medical_book_service)
    return testing.TestClient(app)
