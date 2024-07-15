from unittest.mock import call

from med_sharing_system.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
PATIENT_1 = dict(
    id=1, nickname='test_patient_1', gender='male', age=30, skin_type='сухая',
    about='test_about_1', phone='1234567890'
)
PATIENT_2 = dict(
    id=2, nickname='test_patient_2', gender='female', age=40, skin_type='жирная',
    about='test_about_2', phone='0987654321'
)
PATIENT_3 = dict(
    id=3, nickname='test_patient_3', gender='male', age=50, skin_type='нормальная',
    about='test_about_3', phone='1111111111'
)
PATIENT_LIST: list[dict] = [PATIENT_1, PATIENT_2, PATIENT_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGetById:
    def test__on_get_by_id(self, patient_service, client):
        # Setup
        returned_patient = dtos.Patient(**PATIENT_1)
        patient_id = returned_patient.id
        patient_service.get.return_value = returned_patient

        # Call
        response = client.simulate_get(f'/patients/{patient_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_patient.dict(exclude_none=True,
                                                      exclude_unset=True)
        assert patient_service.method_calls == [call.get(str(patient_id))]


class TestOnGet:
    def test__on_get(self, patient_service, client):
        # Setup
        service_output = [dtos.Patient(**patient) for patient in PATIENT_LIST]
        patient_service.find.return_value = service_output
        filter_params = schemas.FindPatients(
            gender='male',
            age_from=18,
            age_to=50,
            skin_type='сухая',
            sort_field='id',
            sort_direction='asc',
            limit=10,
            offset=0,
        )
        url: str = (
            f'/patients?'
            f'gender={filter_params.gender}&'
            f'age_from={filter_params.age_from}&'
            f'age_to={filter_params.age_to}&'
            f'skin_type={filter_params.skin_type}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}'
        )

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == [
            patient.dict(exclude_none=True, exclude_unset=True)
            for patient in service_output
        ]
        assert patient_service.method_calls == [call.find(filter_params)]

    def test__on_get_default(self, patient_service, client):
        # Setup
        returned_patients = [dtos.Patient(**patient) for patient in PATIENT_LIST]
        patient_service.find.return_value = returned_patients
        filter_params = schemas.FindPatients()

        # Call
        response = client.simulate_get('/patients')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            patient.dict(exclude_none=True, exclude_unset=True)
            for patient in returned_patients
        ]
        assert patient_service.method_calls == [call.find(filter_params)]


class TestOnPostNew:
    def test__on_post_new(self, patient_service, client):
        # Setup
        new_patient_info = dtos.NewPatientInfo(
            nickname='test_patient_4', gender='male', age=60, skin_type='сухая',
            about='test_about_4', phone='2222222222')
        service_output = dtos.Patient(**new_patient_info.dict(), id=4)
        patient_service.add.return_value = service_output

        # Call
        response = client.simulate_post('/patients/new', json=new_patient_info.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert patient_service.method_calls == [call.add(new_patient_info)]


class TestOnPutById:
    def test__on_put_by_id(self, patient_service, client):
        # Setup
        updated_patient_info = dtos.UpdatedPatientInfo(**PATIENT_1)
        service_output = dtos.Patient(**updated_patient_info.dict())
        patient_service.change.return_value = service_output

        # Call
        response = client.simulate_put(f'/patients/{updated_patient_info.id}',
                                       json=updated_patient_info.dict())

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert patient_service.method_calls == [call.change(updated_patient_info)]


class TestOnDeleteById:
    def test__on_delete_by_id(self, patient_service, client):
        # Setup
        service_output = dtos.Patient(**PATIENT_1)
        patient_service.delete.return_value = service_output

        # Call
        response = client.simulate_delete(f'/patients/{service_output.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert patient_service.method_calls == [call.delete(f'{service_output.id}')]
