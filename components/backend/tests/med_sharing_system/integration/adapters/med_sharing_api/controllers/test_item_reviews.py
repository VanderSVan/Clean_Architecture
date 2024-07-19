from unittest.mock import call

from med_sharing_system.application import dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
REVIEW_1 = dict(id=1, item_id=1, is_helped=True, item_rating=9.5, item_count=5,
                usage_period=7776000)
REVIEW_2 = dict(id=2, item_id=1, is_helped=False, item_rating=3.5, item_count=3,
                usage_period=2592000)
REVIEW_3 = dict(id=3, item_id=2, is_helped=True, item_rating=7.5, item_count=2,
                usage_period=7776000)

REVIEW_LIST: list[dict] = [REVIEW_1, REVIEW_2, REVIEW_3]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGetById:
    def test__on_get_by_id(self, item_review_service, client):
        # Setup

        returned_review = dtos.ItemReview(**REVIEW_1)
        review_id: int = returned_review.id
        item_review_service.get_review.return_value = returned_review

        # Call
        response = client.simulate_get(f'/item_reviews/{review_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_review.dict(exclude_none=True,
                                                     exclude_unset=True)
        assert item_review_service.method_calls == [call.get_review(f'{review_id}')]


class TestOnGet:
    def test__on_get(self, item_review_service, client):
        # Setup
        returned_reviews = [dtos.ItemReview(**review) for review in REVIEW_LIST]
        item_review_service.find_reviews.return_value = returned_reviews
        filter_params = schemas.FindItemReviews(
            item_ids=[1, 2],
            patient_id=1,
            is_helped=True,
            min_rating=2,
            max_rating=9,
            sort_field='id',
            sort_direction='asc',
            limit=10,
            offset=0,
            exclude_review_fields=['item_id', 'usage_period']
        )
        exclude_review_fields: str = ','.join(filter_params.exclude_review_fields)
        url: str = (
            f'/item_reviews?'
            f'item_ids={filter_params.item_ids[0]}&'
            f'item_ids={filter_params.item_ids[1]}&'
            f'patient_id={filter_params.patient_id}&'
            f'is_helped={filter_params.is_helped}&'
            f'min_rating={filter_params.min_rating}&'
            f'max_rating={filter_params.max_rating}&'
            f'sort_field={filter_params.sort_field}&'
            f'sort_direction={filter_params.sort_direction}&'
            f'limit={filter_params.limit}&'
            f'offset={filter_params.offset}&'
            f'exclude_review_fields={exclude_review_fields}'
        )

        # Call
        response = client.simulate_get(url)

        # Assert
        assert response.status_code == 200
        assert response.json == [
            review.dict(exclude_none=True, exclude_unset=True)
            for review in returned_reviews if review is not None
        ]
        called_filter_params = item_review_service.method_calls[0][1][0]
        assert (
            called_filter_params.dict(exclude={'exclude_review_fields'}) ==
            filter_params.dict(exclude={'exclude_review_fields'})
        )
        assert set(called_filter_params.exclude_review_fields) == set(
            filter_params.exclude_review_fields
        )

    def test_on_get_default(self, item_review_service, client):
        # Setup
        returned_reviews = [dtos.ItemReview(**review) for review in REVIEW_LIST]
        item_review_service.find_reviews.return_value = returned_reviews
        filter_params = schemas.FindItemReviews(exclude_review_fields=[])

        # Call
        response = client.simulate_get('/item_reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            review.dict(exclude_none=True, exclude_unset=True)
            for review in returned_reviews if review is not None
        ]
        assert item_review_service.method_calls == [call.find_reviews(filter_params)]


class TestOnPostNew:
    def test__on_post_new(self, item_review_service, client):
        # Setup
        new_review_info = dtos.NewItemReviewInfo(
            item_id=1, patient_id=1, is_helped=True, item_rating=9.5, item_count=5,
            usage_period=7776000
        )
        returned_review = dtos.ItemReview(**new_review_info.dict(), id=4)
        item_review_service.add.return_value = returned_review

        # Call
        response = client.simulate_post('/item_reviews/new', json=new_review_info.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == returned_review.dict(
            exclude_none=True, exclude_unset=True
        )
        assert item_review_service.method_calls == [
            call.add(new_review_info)
        ]


class TestOnPutById:
    def test__on_put_by_id(self, item_review_service, client):
        # Setup
        updated_review_info = dtos.UpdatedItemReviewInfo(**REVIEW_1)
        returned_review = dtos.ItemReview(**REVIEW_1)
        item_review_service.change.return_value = returned_review

        # Call
        response = client.simulate_put(f'/item_reviews/{updated_review_info.id}',
                                       json=updated_review_info.dict())

        # Assert
        assert response.status_code == 200
        assert response.json == returned_review.dict(
            exclude_none=True, exclude_unset=True
        )
        assert item_review_service.method_calls == [
            call.change(updated_review_info)
        ]


class TestDeleteById:
    def test__on_delete_by_id(self, item_review_service, client):
        # Setup
        returned_review = dtos.ItemReview(**REVIEW_1)
        item_review_service.delete.return_value = returned_review

        # Call
        response = client.simulate_delete(f'/item_reviews/{returned_review.id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_review.dict(
            exclude_none=True, exclude_unset=True
        )
        assert item_review_service.method_calls == [call.delete(f'{returned_review.id}')]
