from unittest.mock import call

from simple_medication_selection.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
CATEGORY_1 = dict(id=1, name='Категория 1')
CATEGORY_2 = dict(id=2, name='Категория 2')
CATEGORY_3 = dict(id=3, name='Категория 3')
CATEGORY_LIST: list[dict] = [CATEGORY_1, CATEGORY_2, CATEGORY_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, item_category_service, client):
        # Setup
        service_output = [
            dtos.ItemCategory(**category) for category in CATEGORY_LIST
        ]
        item_category_service.find.return_value = service_output
        filter_params = schemas.FindItemCategories(
            keywords='Категория',
            sort_field='id',
            sort_direction='asc',
            limit=10,
            offset=0,
        )
        url: str = (
            f'/item_categories?'
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
        assert item_category_service.method_calls == [call.find(filter_params)]

    def test__on_get_default(self, item_category_service, client):
        # Setup
        service_output = [dtos.ItemCategory(**category)
                          for category in CATEGORY_LIST]
        item_category_service.find.return_value = service_output
        filter_params = schemas.FindItemCategories()

        # Call
        response = client.simulate_get('/item_categories')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            category.dict(exclude_none=True, exclude_unset=True)
            for category in service_output
        ]
        assert item_category_service.method_calls == [call.find(filter_params)]


class TestOnGetById:
    def test__on_get_by_id(self, item_category_service, client):
        # Setup
        service_output = dtos.ItemCategory(**CATEGORY_1)
        item_category_service.get.return_value = service_output
        url: str = f'/item_categories/{CATEGORY_1["id"]}'

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == service_output
        assert item_category_service.method_calls == [call.get(str(CATEGORY_1["id"]))]


class TestOnPostNew:
    def test__on_post_new(self, item_category_service, client):
        # Setup
        service_input = dtos.NewItemCategoryInfo(name='Новая категория')
        service_output = dtos.ItemCategory(**CATEGORY_1)
        item_category_service.add.return_value = service_output

        # Call
        response = client.simulate_post('/item_categories/new', json=service_input.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_category_service.method_calls == [call.add(service_input)]


class TestOnPutById:
    def test__on_put_by_id(self, item_category_service, client):
        # Setup
        service_input = dtos.ItemCategory(id=1, name='Новая категория')
        service_output = dtos.ItemCategory(**CATEGORY_1)
        item_category_service.change.return_value = service_output

        # Call
        response = client.simulate_put(f'/item_categories/{service_output.id}',
                                       json=service_input.dict())

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_category_service.method_calls == [call.change(service_input)]


class TestOnDeleteById:
    def test__on_delete_by_id(self, item_category_service, client):
        # Setup
        service_output = dtos.ItemCategory(**CATEGORY_1)
        item_category_service.delete.return_value = service_output

        # Call
        response = client.simulate_delete(f'/item_categories/{service_output.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == service_output.dict(exclude_none=True, exclude_unset=True)
        assert item_category_service.method_calls == [call.delete(f'{service_output.id}')]
