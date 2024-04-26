from unittest.mock import Mock, call

import pytest

from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def reviews_repo() -> Mock:
    return Mock(interfaces.ItemReviewsRepo)


@pytest.fixture(scope='function')
def items_repo() -> Mock:
    return Mock(interfaces.TreatmentItemsRepo)


@pytest.fixture(scope='function')
def service(reviews_repo, items_repo) -> services.ItemReview:
    return services.ItemReview(item_reviews_repo=reviews_repo,
                               items_repo=items_repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestGetReview:
    @pytest.mark.parametrize("returned_entity", [
        dtos.ItemReview(
            id=1, item_id=1, is_helped=True, item_rating=8, item_count=2,
            usage_period=7776000
        )
    ])
    def test__get_review(self, returned_entity, service, reviews_repo, items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = returned_entity
        review_id = 1

        # Call
        result = service.get_review(review_id=review_id)

        # Assert
        assert reviews_repo.method_calls == [call.fetch_by_id(review_id)]
        assert result == returned_entity
        assert items_repo.method_calls == []


class TestFindReviews:
    @pytest.mark.parametrize(
        "item_ids, patient_id, is_helped, min_rating, max_rating, repo_method",
        [
            ([1, 2], 1, True, 3.0, 8.5,
             'fetch_by_items_patient_helped_status_and_rating'),
            ([1, 2], 1, True, None, 8.5,
             'fetch_by_items_patient_helped_status_and_rating'),
            ([1, 2], 1, True, 3.0, None,
             'fetch_by_items_patient_helped_status_and_rating'),
            ([1, 2], 1, False, 3.0, 8.5,
             'fetch_by_items_patient_helped_status_and_rating'),
            ([1, 2], 1, False, None, 8.5,
             'fetch_by_items_patient_helped_status_and_rating'),
            ([1, 2], 1, False, 3.0, None,
             'fetch_by_items_patient_helped_status_and_rating'),

            (None, 1, True, 3.0, 8.5, 'fetch_by_patient_helped_status_and_rating'),
            (None, 1, True, None, 8.5, 'fetch_by_patient_helped_status_and_rating'),
            (None, 1, True, 3.0, None, 'fetch_by_patient_helped_status_and_rating'),
            (None, 1, False, 3.0, 8.5, 'fetch_by_patient_helped_status_and_rating'),
            (None, 1, False, None, 8.5, 'fetch_by_patient_helped_status_and_rating'),
            (None, 1, False, 3.0, None, 'fetch_by_patient_helped_status_and_rating'),

            ([1, 2], None, True, 3.0, 8.5, 'fetch_by_items_helped_status_and_rating'),
            ([1, 2], None, True, 3.0, None, 'fetch_by_items_helped_status_and_rating'),
            ([1, 2], None, True, None, 8.5, 'fetch_by_items_helped_status_and_rating'),
            ([1, 2], None, False, 3.0, 8.5, 'fetch_by_items_helped_status_and_rating'),
            ([1, 2], None, False, 3.0, None, 'fetch_by_items_helped_status_and_rating'),
            ([1, 2], None, False, None, 8.5, 'fetch_by_items_helped_status_and_rating'),

            ([1, 2], 1, None, 3.0, 8.5, 'fetch_by_items_patient_and_rating'),
            ([1, 2], 1, None, 3.0, None, 'fetch_by_items_patient_and_rating'),
            ([1, 2], 1, None, None, 8.5, 'fetch_by_items_patient_and_rating'),

            ([1, 2], 1, True, None, None, 'fetch_by_items_patient_and_helped_status'),
            ([1, 2], 1, False, None, None, 'fetch_by_items_patient_and_helped_status'),

            (None, None, True, 3.0, 8.5, 'fetch_by_helped_status_and_rating'),
            (None, None, True, None, 8.5, 'fetch_by_helped_status_and_rating'),
            (None, None, True, 3.0, None, 'fetch_by_helped_status_and_rating'),
            (None, None, False, 3.0, 8.5, 'fetch_by_helped_status_and_rating'),
            (None, None, False, None, 8.5, 'fetch_by_helped_status_and_rating'),
            (None, None, False, 3.0, None, 'fetch_by_helped_status_and_rating'),

            (None, 1, None, 3.0, 8.5, 'fetch_by_patient_and_rating'),
            (None, 1, None, 3.0, None, 'fetch_by_patient_and_rating'),
            (None, 1, None, None, 8.5, 'fetch_by_patient_and_rating'),

            (None, 1, True, None, None, 'fetch_by_patient_and_helped_status'),
            (None, 1, False, None, None, 'fetch_by_patient_and_helped_status'),

            ([1, 2], None, None, 3.0, 8.5, 'fetch_by_items_and_rating'),
            ([1, 2], None, None, 3.0, None, 'fetch_by_items_and_rating'),
            ([1, 2], None, None, None, 8.5, 'fetch_by_items_and_rating'),

            ([1, 2], None, True, None, None, 'fetch_by_items_and_helped_status'),
            ([1, 2], None, False, None, None, 'fetch_by_items_and_helped_status'),

            ([1, 2], 1, None, None, None, 'fetch_by_items_and_patient'),

            (None, None, None, 3.0, 8.5, 'fetch_by_rating'),
            (None, None, None, 3.0, None, 'fetch_by_rating'),
            (None, None, None, None, 8.5, 'fetch_by_rating'),

            (None, None, True, None, None, 'fetch_by_helped_status'),
            (None, None, False, None, None, 'fetch_by_helped_status'),

            (None, 1, None, None, None, 'fetch_by_patient'),

            ([1, 2], None, None, None, None, 'fetch_by_items'),

            (None, None, None, None, None, 'fetch_all'),
        ])
    def test__find_reviews(self, item_ids, patient_id, is_helped, min_rating, max_rating,
                           repo_method, service, reviews_repo, items_repo):
        # Setup
        filter_params = schemas.FindItemReviews(
            item_ids=item_ids, patient_id=patient_id, is_helped=is_helped,
            min_rating=min_rating, max_rating=max_rating
        )
        repo_output = [
            dtos.ItemReview(
                id=1, item_id=1, is_helped=True, item_rating=8, item_count=2,
                usage_period=7776000
            )
        ]
        getattr(reviews_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_reviews(filter_params=filter_params)

        # Assert
        getattr(reviews_repo, repo_method).assert_called_once_with(filter_params)
        assert result == repo_output
        assert items_repo.method_calls == []


class TestAdd:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.ItemReview(
                item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.NewItemReviewInfo(
                item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            )
        )
    ])
    def test__add_new_review(self, new_entity, dto, created_entity, service,
                             reviews_repo, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = dto.item_id
        reviews_repo.add.return_value = created_entity

        # Call
        result = service.add(new_review_info=dto)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_id(dto.item_id, False), call.update_avg_rating(dto.item_id)
        ]
        assert reviews_repo.method_calls == [call.add(new_entity)]
        assert result == created_entity

    @pytest.mark.parametrize("dto", [
        (
            dtos.NewItemReviewInfo(
                item_id=10001, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            )
        )
    ])
    def test__item_not_found(self, dto, service, reviews_repo, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None

        # Call
        with pytest.raises(errors.TreatmentItemNotFound):
            service.add(new_review_info=dto)

        # Assert
        assert reviews_repo.method_calls == []
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id, False)]


class TestChange:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.UpdatedItemReviewInfo(
                id=1, item_id=10, is_helped=True, item_rating=9.5, item_count=5,
                usage_period=2592000
            ),
            entities.ItemReview(
                id=1, item_id=10, is_helped=True, item_rating=9.5, item_count=5,
                usage_period=2592000
            )
        )
    ])
    def test__change_review(self, existing_entity, dto, updated_entity, service,
                            reviews_repo, items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = existing_entity
        items_repo.fetch_by_id.return_value = dto.item_id

        # Call
        result = service.change(new_review_info=dto)

        # Assert
        assert reviews_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert items_repo.method_calls == [
            call.fetch_by_id(dto.item_id, False),
            call.fetch_by_id(dto.item_id, False),
            call.update_avg_rating(dto.item_id)
        ]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.UpdatedItemReviewInfo(
            id=1,
            item_id=10001, is_helped=False, item_rating=4, item_count=2,
            usage_period=2592000
        )
    ])
    def test__review_not_found(self, dto, service, reviews_repo, items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemReviewNotFound):
            service.change(new_review_info=dto)

        assert reviews_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert items_repo.method_calls == []

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.UpdatedItemReviewInfo(
                id=1,
                item_id=10001
            )
        )
    ])
    def test__item_not_found(self, existing_entity, dto, service, reviews_repo,
                             items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = existing_entity
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.change(new_review_info=dto)

        assert reviews_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id, False)]


class TestDelete:
    @pytest.mark.parametrize("existing_entity, removed_entity", [
        (
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
        )
    ])
    def test__delete_review(self, existing_entity, removed_entity, service, reviews_repo,
                            items_repo):
        # Setup
        review_id = 1
        reviews_repo.fetch_by_id.return_value = existing_entity
        reviews_repo.remove.return_value = removed_entity

        # Call
        result = service.delete(review_id=review_id)

        # Assert
        assert reviews_repo.method_calls == [call.fetch_by_id(existing_entity.id),
                                             call.remove(existing_entity)]
        assert items_repo.method_calls == []
        assert result == removed_entity

    def test__review_not_found(self, service, reviews_repo, items_repo):
        # Setup
        review_id = 1
        reviews_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemReviewNotFound):
            service.delete(review_id=review_id)

        assert reviews_repo.method_calls == [call.fetch_by_id(review_id)]
        assert items_repo.method_calls == []
