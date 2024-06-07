from unittest.mock import call

from simple_medication_selection.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
SYMPTOM_1 = dict(id=1, name='Симптом 1')
SYMPTOM_2 = dict(id=2, name='Симптом 2')
SYMPTOM_3 = dict(id=3, name='Симптом 3')
SYMPTOM_LIST = [SYMPTOM_1, SYMPTOM_2, SYMPTOM_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, symptom_service, client):
        # Setup
        result_output: list[dtos.Symptom] = [
            dtos.Symptom(**symptom_info) for symptom_info in SYMPTOM_LIST
        ]
        symptom_service.find_symptoms.return_value = result_output
        filter_params = schemas.FindSymptoms(keywords='Симптом',
                                             sort_field='id',
                                             sort_direction='asc',
                                             limit=10,
                                             offset=0)

        # Call
        response = client.simulate_get(
            '/symptoms?'
            f'keywords={filter_params.keywords}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}'
        )

        # Assert
        assert response.status_code == 200
        assert response.json == [symptom.dict(exclude_none=True, exclude_unset=True)
                                 for symptom in result_output]
        assert symptom_service.method_calls == [call.find_symptoms(filter_params)]

    def test__on_get_default(self, symptom_service, client):
        # Call
        result_output: list[dtos.Symptom] = [
            dtos.Symptom(**symptom_info) for symptom_info in SYMPTOM_LIST
        ]
        symptom_service.find_symptoms.return_value = result_output
        filter_params = schemas.FindSymptoms()
        response = client.simulate_get('/symptoms')

        assert response.status_code == 200
        assert response.json == [symptom.dict(exclude_none=True, exclude_unset=True)
                                 for symptom in result_output]
        assert symptom_service.method_calls == [call.find_symptoms(filter_params)]


class TestOnGetById:
    def test__on_get_by_id(self, symptom_service, client):
        # Setup
        service_output = dtos.Symptom(**SYMPTOM_1)
        symptom_service.get.return_value = service_output

        # Call
        response = client.simulate_get('/symptoms/1')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert symptom_service.method_calls == [call.get('1')]


class TestOnPostNew:
    def test__on_post(self, symptom_service, client):
        # Setup
        service_output = dtos.Symptom(**SYMPTOM_2)
        symptom_service.add.return_value = service_output

        # Call
        response = client.simulate_post('/symptoms/new', json=SYMPTOM_2)

        # Assert
        assert response.status_code == 201
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert symptom_service.method_calls == [
            call.add(dtos.NewSymptomInfo(**SYMPTOM_2))
        ]


class TestOnPutById:
    def test__on_put(self, symptom_service, client):
        # Setup
        service_output = dtos.Symptom(**SYMPTOM_3)
        symptom_service.change.return_value = service_output
        symptom_id = SYMPTOM_3['id']

        # Call
        response = client.simulate_put(f'/symptoms/{symptom_id}', json=SYMPTOM_3)

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert symptom_service.method_calls == [call.change(dtos.Symptom(**SYMPTOM_3))]


class TestOnDeleteById:
    def test__on_delete(self, symptom_service, client):
        # Setup
        service_output = dtos.Symptom(**SYMPTOM_1)
        symptom_service.delete.return_value = service_output

        # Call
        response = client.simulate_delete('/symptoms/1')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert symptom_service.method_calls == [call.delete('1')]
