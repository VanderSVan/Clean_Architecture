from unittest.mock import call

from med_sharing_system.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
ITEM_1 = dict(
    id=1,
    title='Продукт 1',
    price=1000.5,
    description='Описание 1',
    category_id=1,
    type_id=1,
    avg_rating=7.75,
    reviews=[
        dict(id=1, item_id=1, is_helped=True, item_rating=9.5, item_count=5,
             usage_period=7776000),
        dict(id=2, item_id=1, is_helped=False, item_rating=6, item_count=3,
             usage_period=2592000)
    ]
)
ITEM_2 = dict(
    id=2,
    title='Продукт 2',
    price=2000.5,
    description='Описание 2',
    category_id=2,
    type_id=2,
    avg_rating=5,
    reviews=[
        dict(id=3, item_id=2, is_helped=False, item_rating=2, item_count=3,
             usage_period=5184000),
        dict(id=4, item_id=2, is_helped=True, item_rating=8, item_count=4,
             usage_period=2592000)
    ]
)
ITEM_3 = dict(
    id=3,
    title='Продукт 3',
    price=5000,
    description='Описание 3',
    category_id=3,
    type_id=3,
    avg_rating=8.5,
    reviews=[
        dict(id=5, item_id=3, is_helped=True, item_rating=8, item_count=4,
             usage_period=2592000),
        dict(id=6, item_id=3, is_helped=True, item_rating=9, item_count=5,
             usage_period=None)
    ]
)
ITEM_4 = dict(
    id=4,
    title='Процедура 1',
    price=2000,
    description=None,
    category_id=1,
    type_id=1,
    avg_rating=7.5,
    reviews=[
        dict(id=7, item_id=4, is_helped=True, item_rating=7.5, item_count=2,
             usage_period=2592000)
    ]
)
ITEM_LIST: list[dict] = [ITEM_1, ITEM_2, ITEM_3, ITEM_4]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGetById:
    def test__on_get_by_id(self, catalog_service, client):
        # Setup
        returned_item_info = ITEM_1.copy()
        if returned_item_info.get("reviews"):
            del returned_item_info["reviews"]

        returned_item = dtos.TreatmentItem(**returned_item_info)
        item_id = returned_item.id
        catalog_service.get_item.return_value = returned_item

        # Call
        response = client.simulate_get(f'/items/{item_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_item.dict(decode=True)
        assert catalog_service.method_calls == [call.get_item(str(item_id))]


class TestOnGetByIdWithReviews:
    def test__on_get_by_id_with_reviews(self, catalog_service, client):
        # Setup
        item_id = ITEM_2['id']
        catalog_service.get_item_with_reviews.return_value = (
            dtos.TreatmentItemWithReviews(**ITEM_2)
        )
        filter_params = schemas.GetTreatmentItemWithReviews(
            item_id=item_id,
        )

        # Call
        response = client.simulate_get(f'/items/{item_id}/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == ITEM_2
        assert catalog_service.method_calls == [call.get_item_with_reviews(filter_params)]


class TestOnGet:
    def test__on_get(self, catalog_service, client):
        # Setup
        keywords = 'Продукт'
        returned_items = []
        for item in ITEM_LIST:
            returned_item = item.copy()
            if returned_item.get("reviews"):
                del returned_item["reviews"]

            if not returned_item["title"].find(keywords):
                continue

            returned_items.append(dtos.TreatmentItem(**returned_item))

        catalog_service.find_items.return_value = returned_items
        filter_params = schemas.FindTreatmentItems(
            keywords=keywords,
            is_helped=True,
            diagnosis_id=1,
            symptom_ids=[3, 4],
            match_all_symptoms=True,
            min_rating=2,
            max_rating=9,
            min_price=10,
            max_price=10000,
            category_id=3,
            type_id=3,
            sort_field='avg_rating',
            sort_direction='desc',
            limit=10,
            offset=0,
            exclude_item_fields=['title', 'description']
        )
        exclude_item_fields: str = ','.join(filter_params.exclude_item_fields)
        url: str = (
            f'/items?'
            f'keywords={filter_params.keywords}&'
            f'is_helped={filter_params.is_helped}&'
            f'diagnosis_id={filter_params.diagnosis_id}&'
            f'symptom_ids={filter_params.symptom_ids[0]}&'
            f'symptom_ids={filter_params.symptom_ids[1]}&'
            f'match_all_symptoms={filter_params.match_all_symptoms}&'
            f'min_rating={filter_params.min_rating}&'
            f'max_rating={filter_params.max_rating}&'
            f'min_price={filter_params.min_price}&'
            f'max_price={filter_params.max_price}&'
            f'category_id={filter_params.category_id}&'
            f'type_id={filter_params.type_id}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}&'
            f'exclude_item_fields={exclude_item_fields}'
        )

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == [
            item.dict(decode=True, exclude_none=True, exclude_unset=True)
            for item in returned_items if item is not None
        ]
        called_filter_params = catalog_service.method_calls[0][1][0]
        assert (
            called_filter_params.dict(exclude={'exclude_item_fields'}) ==
            filter_params.dict(exclude={'exclude_item_fields'})
        )
        assert set(called_filter_params.exclude_item_fields) == set(
            filter_params.exclude_item_fields
        )

    def test_on_get_default(self, catalog_service, client):
        # Setup
        returned_items = []
        for item in ITEM_LIST:
            returned_item = item.copy()
            if returned_item.get("reviews"):
                del returned_item["reviews"]

        catalog_service.find_items.return_value = returned_items

        # Call
        response = client.simulate_get('/items')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            item.dict(decode=True, exclude_none=True, exclude_unset=True)
            for item in returned_items if item is not None
        ]


class TestOnGetWithReviews:
    def test__on_get_with_reviews(self, catalog_service, client):
        # Setup
        returned_items = [
            dtos.TreatmentItemWithReviews(**item) for item in ITEM_LIST
        ]

        catalog_service.find_items_with_reviews.return_value = returned_items
        filter_params = schemas.FindTreatmentItemsWithReviews(
            keywords='Продукт',
            is_helped=True,
            diagnosis_id=1,
            symptom_ids=[3, 4],
            match_all_symptoms=True,
            min_rating=2,
            max_rating=9,
            min_price=10,
            max_price=10000,
            category_id=3,
            type_id=3,
            sort_field='avg_rating',
            sort_direction='desc',
            limit=10,
            offset=0,
            exclude_item_fields=['title', 'description'],
            reviews_sort_field='item_rating',
            reviews_sort_direction='desc',
            reviews_limit=10,
            reviews_offset=0,
            exclude_review_fields=['id', 'item_id']
        )
        exclude_review_fields: str = ','.join(filter_params.exclude_review_fields)
        url: str = (
            f'/items/reviews?'
            f'keywords={filter_params.keywords}&'
            f'is_helped={filter_params.is_helped}&'
            f'diagnosis_id={filter_params.diagnosis_id}&'
            f'symptom_ids={filter_params.symptom_ids[0]}&'
            f'symptom_ids={filter_params.symptom_ids[1]}&'
            f'match_all_symptoms={filter_params.match_all_symptoms}&'
            f'min_rating={filter_params.min_rating}&'
            f'max_rating={filter_params.max_rating}&'
            f'min_price={filter_params.min_price}&'
            f'max_price={filter_params.max_price}&'
            f'category_id={filter_params.category_id}&'
            f'type_id={filter_params.type_id}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}&'
            f'exclude_item_fields={filter_params.exclude_item_fields[0]}&'
            f'exclude_item_fields={filter_params.exclude_item_fields[1]}&'
            f'reviews_sort_field={filter_params.reviews_sort_field}&'
            f'reviews_sort_direction={filter_params.reviews_sort_direction}&'
            f'reviews_limit={filter_params.reviews_limit}&'
            f'reviews_offset={filter_params.reviews_offset}&'
            f'exclude_review_fields={exclude_review_fields}'
        )

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == [
            item.dict(decode=True, exclude_none=True, exclude_unset=True)
            for item in returned_items if item is not None
        ]
        called_filter_params = catalog_service.method_calls[0][1][0]
        assert (
            called_filter_params.dict(exclude={'exclude_review_fields',
                                               'exclude_item_fields'}) ==
            filter_params.dict(exclude={'exclude_review_fields',
                                        'exclude_item_fields'})
        )
        assert set(called_filter_params.exclude_review_fields) == set(
            filter_params.exclude_review_fields
        )
        assert set(called_filter_params.exclude_item_fields) == set(
            filter_params.exclude_item_fields
        )

    def test_on_get_with_reviews_default(self, catalog_service, client):
        # Setup
        returned_items = [
            dtos.TreatmentItemWithReviews(**item) for item in ITEM_LIST
        ]

        catalog_service.find_items_with_reviews.return_value = returned_items
        filter_params = schemas.FindTreatmentItemsWithReviews(exclude_item_fields=[],
                                                              exclude_review_fields=[])

        # Call
        response = client.simulate_get('/items/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            item.dict(decode=True, exclude_none=True, exclude_unset=True)
            for item in returned_items if item is not None
        ]
        assert catalog_service.method_calls == [
            call.find_items_with_reviews(filter_params)
        ]


class TestOnPostNew:
    def test__on_post(self, catalog_service, client):
        # Setup
        ITEM_2["reviews"] = []

        returned_item = dtos.TreatmentItemWithReviews(**ITEM_2)
        catalog_service.add_item.return_value = returned_item

        # Call
        response = client.simulate_post('/items/new', json=ITEM_2)

        # Assert
        assert response.status_code == 201
        assert response.json == returned_item.dict(
            decode=True, exclude_none=True, exclude_unset=True
        )
        assert catalog_service.method_calls == [
            call.add_item(dtos.NewTreatmentItemInfo(**ITEM_2))
        ]


class TestOnPutById:
    def test__on_put_by_id(self, catalog_service, client):
        # Setup
        ITEM_3["reviews"] = []

        returned_item = dtos.TreatmentItemWithReviews(**ITEM_3)
        item_id = returned_item.id
        catalog_service.change_item.return_value = returned_item

        # Call
        response = client.simulate_put(f'/items/{item_id}', json=ITEM_3)

        # Assert
        assert response.status_code == 200
        assert response.json == returned_item.dict(
            decode=True, exclude_none=True, exclude_unset=True
        )
        assert catalog_service.method_calls == [
            call.change_item(dtos.UpdatedTreatmentItemInfo(**ITEM_3))
        ]


class TestOnDeleteById:
    def test__on_delete_by_id(self, catalog_service, client):
        # Setup
        returned_item = dtos.TreatmentItemWithReviews(**ITEM_1)
        item_id = returned_item.id
        catalog_service.delete_item.return_value = returned_item

        # Call
        response = client.simulate_delete(f'/items/{item_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_item.dict(
            decode=True, exclude_none=True, exclude_unset=True
        )
        assert catalog_service.method_calls == [call.delete_item(str(item_id))]
