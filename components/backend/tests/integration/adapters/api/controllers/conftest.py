from unittest.mock import Mock

import pytest
from falcon import testing

from simple_medication_selection.adapters.api.app import create_app
from simple_medication_selection.application import services


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
def client(patient_service,
           symptom_service,
           item_review_service,
           catalog_service,
           medical_book_service):
    app = create_app(patient=patient_service,
                     symptom=symptom_service,
                     item_review=item_review_service,
                     catalog=catalog_service,
                     medical_book=medical_book_service)
    return testing.TestClient(app)
