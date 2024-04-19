from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (
    dtos, entities, errors, interfaces, services, schemas
)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def items_repo() -> Mock:
    return Mock(interfaces.TreatmentItemsRepo)


@pytest.fixture(scope='function')
def reviews_repo() -> Mock:
    return Mock(interfaces.ItemReviewsRepo)


@pytest.fixture(scope='function')
def categories_repo() -> Mock:
    return Mock(interfaces.ItemCategoriesRepo)


@pytest.fixture(scope='function')
def types_repo() -> Mock:
    return Mock(interfaces.ItemTypesRepo)


@pytest.fixture(scope='function')
def service(items_repo,
            reviews_repo,
            categories_repo,
            types_repo
            ) -> services.TreatmentItemCatalog:
    return services.TreatmentItemCatalog(
        items_repo=items_repo,
        item_reviews_repo=reviews_repo,
        item_categories_repo=categories_repo,
        item_types_repo=types_repo
    )


# diagnosis_id, symptom_ids, is_helped, repo_method
filter_params_combinations: list[tuple] = [
    (1, [1, 2], True, 'fetch_by_helped_status_diagnosis_symptoms'),
    (1, [1, 2], False, 'fetch_by_helped_status_diagnosis_symptoms'),

    (1, [1, 2], None, 'fetch_by_diagnosis_and_symptoms'),

    (1, None, True, 'fetch_by_diagnosis_and_helped_status'),
    (1, None, False, 'fetch_by_diagnosis_and_helped_status'),

    (1, None, None, 'fetch_by_diagnosis'),

    (None, [1, 2], True, 'fetch_by_symptoms_and_helped_status'),
    (None, [1, 2], False, 'fetch_by_symptoms_and_helped_status'),

    (None, [1, 2], None, 'fetch_by_symptoms'),

    (None, None, True, 'fetch_by_helped_status'),
    (None, None, False, 'fetch_by_helped_status'),

    (None, None, None, 'fetch_all'),
]


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGetItem:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=2, type_id=3),
            dtos.TreatmentItem(id=1, title="Продукт 1", category_id=2, type_id=3)
        )
    ])
    def test__get_item(self, repo_output, service_output, service, items_repo,
                       reviews_repo, categories_repo, types_repo):
        # Setup
        items_repo.fetch_by_id.return_value = repo_output
        filter_params = schemas.GetTreatmentItem(item_id=repo_output.id)

        # Call
        result = service.get_item(filter_params)

        # Assert
        assert result == service_output
        assert items_repo.method_calls == [call.fetch_by_id(repo_output.id, False)]
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []

    def test__item_not_found(self, service, items_repo, reviews_repo, categories_repo,
                             types_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None
        filter_params = schemas.GetTreatmentItem(item_id=1)

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get_item(filter_params)

        assert items_repo.method_calls == [call.fetch_by_id(filter_params.item_id, False)]
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []


class TestGetItemWithReviews:

    @pytest.mark.parametrize("items_repo_output, service_output", [
        (
            entities.TreatmentItem(
                id=1, title="Продукт 1", category_id=2, type_id=3,
                reviews=[
                    dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                    item_count=5, usage_period=2000000),
                    dtos.ItemReview(id=2, item_id=1, is_helped=False, item_rating=2.5,
                                    item_count=2, usage_period=1000000)
                ]
            ),
            dtos.TreatmentItemWithReviews(
                id=1, title="Продукт 1", category_id=2, type_id=3,
                reviews=[
                    dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                    item_count=5, usage_period=2000000),
                    dtos.ItemReview(id=2, item_id=1, is_helped=False, item_rating=2.5,
                                    item_count=2, usage_period=1000000)
                ]
            )
        )
    ])
    def test__get_items_with_reviews(
        self, items_repo_output, service_output, service, items_repo, reviews_repo,
        categories_repo, types_repo
    ):
        # Setup
        items_repo.fetch_by_id.return_value = items_repo_output
        filter_params = schemas.GetTreatmentItem(item_id=items_repo_output.id,
                                                 reviews_limit=None,
                                                 reviews_offset=None)

        # Call
        result = service.get_item_with_reviews(filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(filter_params.item_id, True)]
        assert result == service_output
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []

    @pytest.mark.parametrize("reviews_limit, reviews_offset, reviews_sort_field", [
        (10, None, None),
        (None, 1, None),
        (None, None, 'item_rating'),
        (10, 1, None),
        (10, None, 'item_rating'),
        (None, 1, 'item_rating'),
        (10, 1, 'item_rating'),
    ])
    def test__with_limit_offset_and_sort(
        self, service, reviews_limit, reviews_offset, reviews_sort_field, items_repo,
        reviews_repo, categories_repo, types_repo
    ):
        # Setup
        items_repo_output = entities.TreatmentItem(
            id=1, title="Продукт 1", category_id=2, type_id=3
        )
        reviews_repo_output = [
            entities.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=5, usage_period=2000000),
            entities.ItemReview(id=2, item_id=1, is_helped=False, item_rating=2.5,
                                item_count=2, usage_period=1000000)
        ]
        service_output = dtos.TreatmentItemWithReviews(
            id=1, title="Продукт 1", category_id=2, type_id=3,
            reviews=[
                dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=7.5,
                                item_count=5, usage_period=2000000),
                dtos.ItemReview(id=2, item_id=1, is_helped=False, item_rating=2.5,
                                item_count=2, usage_period=1000000)
            ]
        )
        items_filter_params = schemas.GetTreatmentItem(
            item_id=items_repo_output.id, reviews_sort_field=reviews_sort_field,
            reviews_limit=reviews_limit, reviews_offset=reviews_offset
        )
        reviews_filter_params = schemas.FindItemReviews(
            item_ids=[items_filter_params.item_id],
            sort_field=items_filter_params.reviews_sort_field,
            sort_direction=items_filter_params.reviews_sort_direction,
            limit=items_filter_params.reviews_limit,
            offset=items_filter_params.reviews_offset
        )
        items_repo.fetch_by_id.return_value = items_repo_output
        reviews_repo.fetch_by_item.return_value = reviews_repo_output

        # Call
        result = service.get_item_with_reviews(items_filter_params)

        # Assert
        assert result == service_output
        assert items_repo.method_calls == [call.fetch_by_id(items_repo_output.id, False)]
        assert reviews_repo.method_calls == [call.fetch_by_item(reviews_filter_params)]
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []

    def test__item_not_found(self, service, items_repo, reviews_repo, categories_repo,
                             types_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None
        filter_params = schemas.GetTreatmentItem(item_id=1)

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get_item_with_reviews(filter_params)

        assert items_repo.method_calls == [call.fetch_by_id(filter_params.item_id, False)]
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []


class TestFindItems:
    @pytest.mark.parametrize("diagnosis_id, symptom_ids, is_helped, repo_method",
                             filter_params_combinations)
    def test__find_items(self, diagnosis_id, symptom_ids, is_helped, repo_method,
                         service, items_repo, reviews_repo, categories_repo, types_repo):
        # Setup
        filter_params = schemas.FindTreatmentItemList(
            diagnosis_id=diagnosis_id, symptom_ids=symptom_ids, is_helped=is_helped
        )
        repo_output = [
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=2, type_id=3),
            entities.TreatmentItem(id=2, title="Продукт 2", category_id=1, type_id=2),
        ]
        service_output = [
            dtos.TreatmentItem(id=1, title="Продукт 1", category_id=2, type_id=3),
            dtos.TreatmentItem(id=2, title="Продукт 2", category_id=1, type_id=2),
        ]
        getattr(items_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert result == service_output
        getattr(items_repo, repo_method).assert_called_once_with(filter_params, False)
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []


class TestFindItemsWithReviews:
    @pytest.mark.parametrize("diagnosis_id, symptom_ids, is_helped, repo_method",
                             filter_params_combinations)
    def test__find_items_with_reviews(
        self, diagnosis_id, symptom_ids, is_helped, repo_method, service, items_repo,
        reviews_repo, categories_repo, types_repo
    ):
        # Setup
        filter_params = schemas.FindTreatmentItemList(
            diagnosis_id=diagnosis_id, symptom_ids=symptom_ids, is_helped=is_helped
        )
        repo_output = [
            entities.TreatmentItem(
                id=1, title="Продукт 1", category_id=2, type_id=3,
                reviews=[
                    entities.ItemReview(id=1, item_id=1, is_helped=True, item_rating=8.0,
                                        item_count=5, usage_period=2000000),
                ]
            ),
            entities.TreatmentItem(
                id=2, title="Продукт 2", category_id=1, type_id=2,
                reviews=[
                    entities.ItemReview(id=2, item_id=2, is_helped=False, item_rating=2.5,
                                        item_count=2, usage_period=1000000),
                ]
            ),
        ]
        service_output = [
            dtos.TreatmentItemWithReviews(
                id=1, title="Продукт 1", category_id=2, type_id=3,
                reviews=[
                    dtos.ItemReview(id=1, item_id=1, is_helped=True, item_rating=8.0,
                                    item_count=5, usage_period=2000000),
                ]
            ),
            dtos.TreatmentItemWithReviews(
                id=2, title="Продукт 2", category_id=1, type_id=2,
                reviews=[
                    dtos.ItemReview(id=2, item_id=2, is_helped=False, item_rating=2.5,
                                    item_count=2, usage_period=1000000),
                ]
            ),

        ]
        getattr(items_repo, repo_method).return_value = repo_output

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert result == service_output
        getattr(items_repo, repo_method).assert_called_once_with(filter_params, True)
        assert reviews_repo.method_calls == []
        assert categories_repo.method_calls == []
        assert types_repo.method_calls == []


class TestAddItem:
    @pytest.mark.parametrize("new_entity, dto, saved_entity", [
        (
            entities.TreatmentItem(title='Продукт 1', category_id=1, type_id=2),
            dtos.NewTreatmentItemInfo(title='Продукт 1', category_id=1, type_id=2),
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
        )
    ])
    def test__create_new_treatment_item(self, new_entity, dto, saved_entity, service,
                                        items_repo, categories_repo, types_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        types_repo.fetch_by_id.return_value = entities.ItemType(id=2, name='Сыворотка')
        items_repo.add.return_value = saved_entity

        # Call
        result = service.add_item(new_item_info=dto)

        # Assert
        assert items_repo.method_calls == [call.add(new_entity)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]
        assert types_repo.method_calls == [call.fetch_by_id(dto.type_id)]
        assert result == saved_entity

    @pytest.mark.parametrize("dto", [
        dtos.NewTreatmentItemInfo(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__category_does_not_exist(self, dto, service, categories_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.add_item(new_item_info=dto)

        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.NewTreatmentItemInfo(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__type_does_not_exist(self, dto, service, categories_repo, types_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        types_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.add_item(new_item_info=dto)

        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]
        assert types_repo.method_calls == [call.fetch_by_id(dto.type_id)]


class TestChangeItem:
    @pytest.mark.parametrize("existing_entity, dto, updated_entity", [
        (
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
            dtos.UpdatedTreatmentItemInfo(id=1, title='Продукт 2', category_id=3,
                                          type_id=11),
            entities.TreatmentItem(id=1, title='Продукт 2', category_id=3, type_id=11),
        )
    ])
    def test__change_treatment_item(self, existing_entity, dto, updated_entity, service,
                                    items_repo, categories_repo, types_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity
        categories_repo.fetch_by_id.return_value = (
            entities.ItemCategory(id=3, name='Уходовая косметика')
        )
        types_repo.fetch_by_id.return_value = entities.ItemType(id=11, name='Крем')

        # Call
        result = service.change_item(new_item_info=dto)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(dto.id, True)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]
        assert types_repo.method_calls == [call.fetch_by_id(dto.type_id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.UpdatedTreatmentItemInfo(id=100, title='Продукт 1', category_id=1,
                                      type_id=10),
    ])
    def test__item_does_not_exist(self, dto, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.change_item(new_item_info=dto)

        assert items_repo.method_calls == [call.fetch_by_id(dto.id, True)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
            dtos.UpdatedTreatmentItemInfo(id=1, title='Продукт 2', category_id=3,
                                          type_id=11),
        )
    ])
    def test__category_does_not_exist(self, existing_entity, dto, service,
                                      items_repo, categories_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity
        categories_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.change_item(new_item_info=dto)

        assert items_repo.method_calls == [call.fetch_by_id(dto.id, True)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
            dtos.UpdatedTreatmentItemInfo(id=1, title='Продукт 2', category_id=3,
                                          type_id=11),
        )
    ])
    def test__type_does_not_exist(self, existing_entity, dto, service, items_repo,
                                  categories_repo, types_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity
        categories_repo.fetch_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        types_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.change_item(new_item_info=dto)

        assert items_repo.method_calls == [call.fetch_by_id(dto.id, True)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]
        assert types_repo.method_calls == [call.fetch_by_id(dto.type_id)]


class TestDeleteItem:
    @pytest.mark.parametrize("existing_entity, removed_entity", [
        (
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=10),
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=10),
        )
    ])
    def test__delete_treatment_item(self, existing_entity, removed_entity, service,
                                    items_repo):
        # Setup
        item_id = 1
        items_repo.fetch_by_id.return_value = existing_entity
        items_repo.remove.return_value = removed_entity

        # Call
        result = service.delete_item(item_id=item_id)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(item_id, True),
                                           call.remove(removed_entity)]
        assert result == removed_entity

    def test__item_does_not_exist(self, service, items_repo):
        # Setup
        item_id = 1
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.delete_item(item_id=item_id)

        assert items_repo.method_calls == [call.fetch_by_id(item_id, True)]
