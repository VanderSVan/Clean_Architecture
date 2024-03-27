from unittest.mock import Mock

import pytest
from falcon import testing

from simple_medication_selection.application import services
from simple_medication_selection.adapters.api.app import create_app


@pytest.fixture(scope='function')
def symptom_service() -> Mock:
    return Mock(services.Symptom)


@pytest.fixture(scope='function')
def catalog_service() -> Mock:
    return Mock(services.TreatmentItemCatalog)


@pytest.fixture(scope='function')
def client(symptom_service, catalog_service):
    app = create_app(symptom=symptom_service, catalog=catalog_service)
    return testing.TestClient(app)

