from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors, interfaces,
                                                     services)


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
def service(reviews_repo, items_repo ) -> services.ItemReview:
    return services.ItemReview(item_reviews_repo=reviews_repo,
                               items_repo=items_repo)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestGetPatientReviewByItem:
    @pytest.mark.parametrize("returned_entity", [
        [
            entities.ItemReview(
                id=2, item_id=1, is_helped=True, item_rating=8, item_count=2,
                usage_period=7776000
            )
        ]
    ])
    def test__get_patient_review_by_item(self, returned_entity, service, reviews_repo,
                                         items_repo):
        # Setup
        reviews_repo.fetch_patient_reviews_by_item.return_value = returned_entity
        default_limit = 10
        default_offset = 0

        # Call
        result = service.get_patient_review_by_item(patient_id=1, item_id=2)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_patient_reviews_by_item(1, 2, default_limit, default_offset)
        ]
        assert result == returned_entity
        assert items_repo.method_calls == []


class TestGetReviewsByItem:
    @pytest.mark.parametrize("returned_entity", [
        [
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            )
        ]
    ])
    def test__get_reviews_by_item(self, returned_entity, service, reviews_repo,
                                  items_repo):
        # Setup
        reviews_repo.fetch_all_by_item_id.return_value = returned_entity
        default_limit = 10
        default_offset = 0

        # Call
        result = service.get_reviews_by_item(item_id=1)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_all_by_item_id(1, default_limit, default_offset)
        ]
        assert result == returned_entity
        assert items_repo.method_calls == []


class TestGetPatientReviews:
    @pytest.mark.parametrize("returned_entity", [
        [
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            )
        ]
    ])
    def test__get_patient_reviews(self, returned_entity, service, reviews_repo,
                                  items_repo):
        # Setup
        reviews_repo.fetch_reviews_by_patient_id.return_value = returned_entity
        default_limit = 10
        default_offset = 0

        # Call
        result = service.get_patient_reviews(patient_id=1)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_reviews_by_patient_id(1, default_limit, default_offset)
        ]
        assert result == returned_entity
        assert items_repo.method_calls == []


class TestAdd:
    @pytest.mark.parametrize("new_entity, dto, created_entity", [
        (
            entities.ItemReview(
                item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.ItemReviewCreateSchema(
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
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id)]
        assert reviews_repo.method_calls == [call.add(new_entity)]
        assert result == created_entity

    @pytest.mark.parametrize("dto", [
        (
            dtos.ItemReviewCreateSchema(
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
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id)]


class TestChange:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.ItemReviewUpdateSchema(
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
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemReviewUpdateSchema(
            id=1,
            item_id=10001, is_helped=False, item_rating=4, item_count=2,
            usage_period=2592000
        )
    ])
    def test__non_existing_review(self, dto, service, reviews_repo, items_repo):
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
            dtos.ItemReviewUpdateSchema(
                id=1,
                item_id=10001
            )
        )
    ])
    def test__non_existing_item(self, existing_entity, dto, service, reviews_repo,
                                items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = existing_entity
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.change(new_review_info=dto)

        assert reviews_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert items_repo.method_calls == [call.fetch_by_id(dto.item_id)]


class TestDelete:
    @pytest.mark.parametrize("existing_entity, dto, removed_entity", [
        (
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
            dtos.ItemReviewDeleteSchema(id=1),
            entities.ItemReview(
                id=1, item_id=1, is_helped=False, item_rating=4, item_count=2,
                usage_period=2592000
            ),
        )
    ])
    def test__delete_review(self, existing_entity, dto, removed_entity, service,
                            reviews_repo, items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = existing_entity
        reviews_repo.remove.return_value = removed_entity

        # Call
        result = service.delete(review_info=dto)

        # Assert
        assert reviews_repo.method_calls == [call.fetch_by_id(existing_entity.id),
                                             call.remove(existing_entity)]
        assert items_repo.method_calls == []
        assert result == removed_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemReviewDeleteSchema(id=1)
    ])
    def test__review_not_found(self, dto, service, reviews_repo, items_repo):
        # Setup
        reviews_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemReviewNotFound):
            service.delete(review_info=dto)

        assert reviews_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert items_repo.method_calls == []
