from unittest.mock import call

from med_sharing_system.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
DIAGNOSIS_1 = dict(id=1, name='Диагноз 1')
DIAGNOSIS_2 = dict(id=2, name='Диагноз 2')
DIAGNOSIS_3 = dict(id=3, name='Диагноз 3')
DIAGNOSIS_LIST: list[dict] = [DIAGNOSIS_1, DIAGNOSIS_2, DIAGNOSIS_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, diagnosis_service, client):
        # Setup
        service_output: list[dtos.Diagnosis] = [
            dtos.Diagnosis(**diagnosis_info) for diagnosis_info in DIAGNOSIS_LIST
        ]
        diagnosis_service.find.return_value = service_output
        filter_params = schemas.FindDiagnoses(
            keywords='Диагноз',
            sort_field='id',
            sort_direction='asc',
            limit=10,
            offset=0,
        )
        url: str = (
            f'/diagnoses?'
            f'keywords={filter_params.keywords}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}'
        )

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == service_output
        assert diagnosis_service.method_calls == [call.find(filter_params)]

    def test__on_get_default(self, diagnosis_service, client):
        # Setup
        service_output: list[dtos.Diagnosis] = [
            dtos.Diagnosis(**diagnosis_info) for diagnosis_info in DIAGNOSIS_LIST
        ]
        diagnosis_service.find.return_value = service_output
        filter_params = schemas.FindDiagnoses()

        # Call
        response = client.simulate_get('/diagnoses')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            diagnosis.dict(exclude_none=True, exclude_unset=True)
            for diagnosis in service_output
        ]
        assert diagnosis_service.method_calls == [call.find(filter_params)]


class TestOnGetById:
    def test__on_get_by_id(self, diagnosis_service, client):
        # Setup
        service_output = dtos.Diagnosis(**DIAGNOSIS_1)
        diagnosis_service.get.return_value = service_output

        # Call
        response = client.simulate_get(f'/diagnoses/{service_output.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert diagnosis_service.method_calls == [call.get(f'{service_output.id}')]


class TestOnPostNew:
    def test__on_post_new(self, diagnosis_service, client):
        # Setup
        service_input = dtos.NewDiagnosisInfo(name='Новый диагноз')
        service_output = dtos.Diagnosis(**DIAGNOSIS_1)
        diagnosis_service.add.return_value = service_output

        # Call
        response = client.simulate_post('/diagnoses/new', json=service_input.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert diagnosis_service.method_calls == [call.add(service_input)]


class TestOnPutById:
    def test__on_put_by_id(self, diagnosis_service, client):
        # Setup
        service_input = dtos.Diagnosis(id=1, name='Новый диагноз')
        service_output = dtos.Diagnosis(**DIAGNOSIS_1)
        diagnosis_service.change.return_value = service_output

        # Call
        response = client.simulate_put(f'/diagnoses/{service_output.id}',
                                       json=service_input.dict())

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert diagnosis_service.method_calls == [
            call.change(service_input)]


class TestOnDeleteById:
    def test__on_delete_by_id(self, diagnosis_service, client):
        # Setup
        service_output = dtos.Diagnosis(**DIAGNOSIS_1)
        diagnosis_service.delete.return_value = service_output

        # Call
        response = client.simulate_delete(f'/diagnoses/{service_output.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert diagnosis_service.method_calls == [call.delete(f'{service_output.id}')]
