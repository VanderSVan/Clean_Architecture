from unittest.mock import Mock, call

import pytest
from falcon import testing

from simple_medication_selection.application import services, entities
from simple_medication_selection.adapters.api.app import create_app

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
SYMPTOM_1 = dict(id=1, name='Симптом 1')
SYMPTOM_2 = dict(id=2, name='Симптом 2')
SYMPTOM_3 = dict(id=3, name='Симптом 3')
SYMPTOM_LIST = [SYMPTOM_1, SYMPTOM_2, SYMPTOM_3]


@pytest.fixture(scope='function')
def service() -> Mock:
    return Mock(services.Symptom)


@pytest.fixture(scope='function')
def client(service):
    app = create_app(symptom=service)
    return testing.TestClient(app)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, service, client):
        # Setup
        service.find_symptoms.return_value = [
            entities.Symptom(**symptom_info) for symptom_info in SYMPTOM_LIST
        ]

        # Call
        response = client.simulate_get(
            '/symptoms?'
            'keywords=Симптом&'
            'sort_field=id&'
            'sort_direction=asc&'
            'limit=10&'
            'offset=0'
        )

        # Assert
        assert response.status_code == 200
        assert response.json == SYMPTOM_LIST
        assert service.method_calls == [call.find_symptoms('Симптом',
                                                           sort_field='id',
                                                           sort_direction='asc',
                                                           limit=10,
                                                           offset=0)]

    def test__invalid_request(self, client):
        # Call
        response = client.simulate_get('/symptoms')

        assert response.status_code == 422
        assert response.json == [{'loc': ['sort_field'],
                                  'msg': 'field required',
                                  'type': 'value_error.missing'},
                                 {'loc': ['sort_direction'],
                                  'msg': 'field required',
                                  'type': 'value_error.missing'}]


class TestOnGetById:
    def test__on_get_by_id(self, service, client):
        # Setup
        service.get.return_value = entities.Symptom(**SYMPTOM_1)

        # Call
        response = client.simulate_get('/symptoms/1')

        # Assert
        assert response.status_code == 200
        assert response.json == SYMPTOM_1
        assert service.method_calls == [call.get('1')]


class TestOnPost:
    def test__on_post(self, service, client):
        # Setup
        service.create.return_value = entities.Symptom(**SYMPTOM_2)

        # Call
        response = client.simulate_post('/symptoms', json=SYMPTOM_2)

        # Assert
        assert response.status_code == 201
        assert response.json == SYMPTOM_2
        assert service.method_calls == [call.create(SYMPTOM_2)]


class TestOnPut:
    def test__on_put(self, service, client):
        # Setup
        service.change.return_value = entities.Symptom(**SYMPTOM_3)

        # Call
        response = client.simulate_put('/symptoms', json=SYMPTOM_3)

        # Assert
        assert response.status_code == 200
        assert response.json == SYMPTOM_3
        assert service.method_calls == [call.change(SYMPTOM_3)]


class TestOnDeleteById:
    def test__on_delete_by_id(self, service, client):
        # Setup
        service.delete.return_value = entities.Symptom(**SYMPTOM_1)

        # Call
        response = client.simulate_delete('/symptoms/1')

        # Assert
        assert response.status_code == 200
        assert response.json == SYMPTOM_1
        assert service.method_calls == [call.delete('1')]
