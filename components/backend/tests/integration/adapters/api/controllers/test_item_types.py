from unittest.mock import call

from simple_medication_selection.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
ITEM_TYPE_1 = dict(id=1, name='Тип 1')
ITEM_TYPE_2 = dict(id=2, name='Тип 2')
ITEM_TYPE_3 = dict(id=3, name='Тип 3')
ITEM_TYPE_LIST: list[dict] = [ITEM_TYPE_1, ITEM_TYPE_2, ITEM_TYPE_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, item_type_service, client):
        # Setup
        service_output = [
            dtos.ItemType(**item_type) for item_type in ITEM_TYPE_LIST
        ]
        item_type_service.find.return_value = service_output
        filter_params = schemas.FindItemTypes(
            keywords='Тип',
            sort_field='id',
            sort_direction='asc',
            limit=10,
            offset=0,
        )
        url: str = (
            f'/item_types?'
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
        assert item_type_service.method_calls == [call.find(filter_params)]

    def test__on_get_default(self, item_type_service, client):
        # Setup
        service_output = [
            dtos.ItemType(**item_type) for item_type in ITEM_TYPE_LIST
        ]
        item_type_service.find.return_value = service_output
        filter_params = schemas.FindItemTypes()

        # Call
        response = client.simulate_get('/item_types')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            item_type.dict(exclude_none=True, exclude_unset=True)
            for item_type in service_output
        ]
        assert item_type_service.method_calls == [call.find(filter_params)]


class TestOnGetById:
    def test__on_get_by_id(self, item_type_service, client):
        # Setup
        service_output = dtos.ItemType(**ITEM_TYPE_1)
        item_type_service.get.return_value = service_output
        url: str = f'/item_types/{service_output.id}'

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == service_output
        assert item_type_service.method_calls == [call.get(str(service_output.id))]


class TestOnPostNew:
    def test__on_post_new(self, item_type_service, client):
        # Setup
        service_input = dtos.NewItemTypeInfo(name='Новый тип')
        service_output = dtos.ItemType(**ITEM_TYPE_1)
        item_type_service.add.return_value = service_output

        # Call
        response = client.simulate_post('/item_types/new', json=service_input.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_type_service.method_calls == [call.add(service_input)]


class TestOnPutById:
    def test__on_put_by_id(self, item_type_service, client):
        # Setup
        service_input = dtos.ItemType(id=1, name='Новый тип')
        service_output = dtos.ItemType(**ITEM_TYPE_1)
        item_type_service.change.return_value = service_output

        # Call
        response = client.simulate_put(f'/item_types/{service_output.id}',
                                       json=service_input.dict())

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_type_service.method_calls == [call.change(service_input)]


class TestOnDeleteById:
    def test__on_delete_by_id(self, item_type_service, client):
        # Setup
        service_output = dtos.ItemType(**ITEM_TYPE_1)
        item_type_service.delete.return_value = service_output

        # Call
        response = client.simulate_delete(f'/item_types/{service_output.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_type_service.method_calls == [call.delete(f'{service_output.id}')]
