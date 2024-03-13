from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors, interfaces,
                                                     services)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def items_repo() -> Mock:
    return Mock(interfaces.TreatmentItemsRepo)


@pytest.fixture(scope='function')
def categories_repo() -> Mock:
    return Mock(interfaces.ItemCategoriesRepo)


@pytest.fixture(scope='function')
def types_repo() -> Mock:
    return Mock(interfaces.ItemTypesRepo)


@pytest.fixture(scope='function')
def service(items_repo,
            categories_repo,
            types_repo
            ) -> services.TreatmentItemCatalog:
    return services.TreatmentItemCatalog(
        items_repo=items_repo,
        item_categories_repo=categories_repo,
        item_types_repo=types_repo
    )


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGetItem:
    @pytest.mark.parametrize("existing_entity", [
        entities.TreatmentItem(
            id=1, title="Продукт 1", category_id=2, type_id=3
        )
    ])
    def test__get_existing_treatment_item(self, existing_entity, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity

        # Call
        result = service.get_item(item_id=existing_entity.id)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(existing_entity.id)]
        assert result == existing_entity

    def test__get_non_existing_treatment_item(self, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get_item(item_id=1)

        assert items_repo.method_calls == [call.fetch_by_id(1)]


class TestFindItems:
    @pytest.mark.parametrize("keyword, result_output", [
        (
            "Продукт",
            [dtos.ItemGetSchema(id=2, title="Продукт 2", price=None, description=None,
                                category_id=2, type_id=3, avg_rating=7.5),
             dtos.ItemGetSchema(id=3, title="Продукт 3", price=1500.00,
                                description="Some description", category_id=3, type_id=4,
                                avg_rating=8.0),
             dtos.ItemGetSchema(id=4, title="Продукт 4", price=2000.00, description=None,
                                category_id=4, type_id=5, avg_rating=None)]
        )
    ])
    def test__with_keywords(self, keyword, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_keywords.return_value = result_output
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items(keywords="Продукт")

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_keywords("Продукт", default_sort_field, default_sort_direction,
                                   default_limit, default_offset)
        ]
        assert result == result_output

    @pytest.mark.parametrize("result_output", [
        (
            [dtos.ItemGetSchema(id=1, title="Процедура 1", price=None, description=None,
                                category_id=1, type_id=2, avg_rating=7.5),
             dtos.ItemGetSchema(id=2, title="Продукт 2", price=1500.00,
                                description="Some description", category_id=2,
                                type_id=3, avg_rating=8.0),
             dtos.ItemGetSchema(id=3, title="Продукт 3", price=2000.00, description=None,
                                category_id=3, type_id=4, avg_rating=None)]
        )
    ])
    def test__without_keywords(self, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items()

        # Assert
        assert items_repo.method_calls == [
            call.fetch_all(default_sort_field, default_sort_direction, default_limit,
                           default_offset)
        ]
        assert result == result_output


class TestFindItemsWithReviews:
    @pytest.mark.parametrize("keyword, result_output", [
        (
            "Продукт",
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3,
                                    avg_rating=7.75,
                                    reviews=[
                                        entities.ItemReview(id=1,
                                                            item_id=2,
                                                            is_helped=True,
                                                            item_rating=8.0,
                                                            item_count=5,
                                                            usage_period=7776000),
                                        entities.ItemReview(id=2,
                                                            item_id=2,
                                                            is_helped=True,
                                                            item_rating=7.5,
                                                            item_count=2,
                                                            usage_period=2592000),
                                    ]),
             entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4),
             entities.TreatmentItem(id=4, title="Продукт 4", category_id=4, type_id=5)]
        )
    ])
    def test__with_keywords(self, keyword, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_keywords_with_reviews.return_value = result_output
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_with_reviews(keywords="Продукт")

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_keywords_with_reviews("Продукт", default_sort_field,
                                                default_sort_direction,
                                                default_limit, default_offset)
        ]
        assert result == result_output

    @pytest.mark.parametrize("result_output", [
        (
            [entities.TreatmentItem(id=1, title="Процедура 1", category_id=1, type_id=2,
                                    avg_rating=6.25,
                                    reviews=[
                                        entities.ItemReview(id=1,
                                                            item_id=1,
                                                            is_helped=True,
                                                            item_rating=8.0,
                                                            item_count=5,
                                                            usage_period=7776000),
                                        entities.ItemReview(id=2,
                                                            item_id=1,
                                                            is_helped=True,
                                                            item_rating=7.5,
                                                            item_count=2,
                                                            usage_period=2592000),
                                    ]),
             entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3),
             entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4)]
        )
    ])
    def test__without_keywords(self, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all_with_reviews.return_value = result_output
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_with_reviews()

        # Assert
        assert items_repo.method_calls == [
            call.fetch_all_with_reviews(default_sort_field, default_sort_direction,
                                        default_limit, default_offset)
        ]
        assert result == result_output


class TestFindItemsByCategory:
    @pytest.mark.parametrize("repo_output", [
        (
            [entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)],
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=1, type_id=3)]
        )
    ])
    def test__find_items_by_category(self, repo_output, service, items_repo):
        # Setup
        items_repo.fetch_by_category.return_value = repo_output
        category_id = 1
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_category(category_id=category_id)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_category(category_id, default_sort_field,
                                   default_sort_direction, default_limit,
                                   default_offset)
        ]
        assert result == repo_output


class TestFindItemsByType:
    @pytest.mark.parametrize("repo_output", [
        (
            [entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)],
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=2)]
        )
    ])
    def test__find_items_by_type(self, repo_output, service, items_repo):
        # Setup
        items_repo.fetch_by_type.return_value = repo_output
        type_id = 1
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_type(type_id=type_id)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_type(type_id, default_sort_field, default_sort_direction,
                               default_limit, default_offset)
        ]
        assert result == repo_output


class TestFindItemsByRating:
    @pytest.mark.parametrize("repo_output", [
        (
            [
                dtos.ItemGetSchema(id=3, title='Продукт 3', price=2000.0,
                                   description=None, category_id=3, type_id=4,
                                   avg_rating=9.5),
                dtos.ItemGetSchema(id=2, title='Продукт 2', price=None,
                                   description=None, category_id=2, type_id=3,
                                   avg_rating=6.25),
                dtos.ItemGetSchema(id=1, title='Продукт 1', price=None,
                                   description='Описание 1', category_id=1, type_id=2,
                                   avg_rating=None)
            ]
        )
    ])
    def test__find_items_by_rating(self, repo_output, service, items_repo):
        # Setup
        items_repo.fetch_by_rating.return_value = repo_output
        min_rating = 1.5
        max_rating = 10
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_rating(min_rating=min_rating,
                                              max_rating=max_rating)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_rating(min_rating, max_rating, default_sort_field,
                                 default_sort_direction, default_limit, default_offset)
        ]
        assert result == repo_output


class TestFindItemsByHelpedStatus:
    @pytest.mark.parametrize("helped_status, repo_output", [
        (
            True,
            [dtos.ItemWithHelpedStatusGetSchema(id=1, title="Продукт 1", price=1000.0,
                                                description="Описание 1", category_id=1,
                                                type_id=2, avg_rating=10.0,
                                                is_helped=True)]
        ),
        (
            False,
            [dtos.ItemWithHelpedStatusGetSchema(id=2, title="Продукт 2", price=2000.0,
                                                description="Описание 2", category_id=2,
                                                type_id=3, avg_rating=7.5,
                                                is_helped=False)]
        )
    ])
    def test__helped_status(self, helped_status, repo_output, service, items_repo):
        # Setup
        items_repo.fetch_by_helped_status.return_value = repo_output
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_helped_status(is_helped=helped_status)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_helped_status(helped_status, default_sort_field,
                                        default_sort_direction, default_limit,
                                        default_offset)
        ]
        assert result == repo_output


class TestFindItemsBySymptomAndHelpedStatus:
    @pytest.mark.parametrize("repo_output", [
        [
            entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4),
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2),
        ]
    ])
    def test__find_items_by_symptoms_and_helped_status(self, repo_output, service,
                                                       items_repo):
        # Setup
        items_repo.fetch_by_symptoms_and_helped_status.return_value = repo_output
        symptom_ids = [1, 2, 3, 4]
        default_helped_status = True
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids
        )

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_symptoms_and_helped_status(symptom_ids,
                                                     default_helped_status,
                                                     default_sort_field,
                                                     default_sort_direction,
                                                     default_limit,
                                                     default_offset)
        ]
        assert result == repo_output


class TestFindItemsByDiagnosisAndHelpedStatus:
    @pytest.mark.parametrize("repo_output", [
        [
            entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3),
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)
        ]
    ])
    def test__find_items_by_diagnosis_and_helped_status(self, repo_output, service,
                                                        items_repo):
        # Setup
        items_repo.fetch_by_diagnosis_and_helped_status.return_value = repo_output
        diagnosis_id = 1
        default_helped_status = True
        default_sort_field = 'avg_rating'
        default_sort_direction = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items_by_diagnosis_and_helped_status(
            diagnosis_id=diagnosis_id
        )

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_diagnosis_and_helped_status(diagnosis_id,
                                                      default_helped_status,
                                                      default_sort_field,
                                                      default_sort_direction,
                                                      default_limit,
                                                      default_offset)
        ]
        assert result == repo_output


class TestAddItem:
    @pytest.mark.parametrize("new_entity, dto, saved_entity", [
        (
            entities.TreatmentItem(title='Продукт 1', category_id=1, type_id=2),
            dtos.ItemCreateSchema(title='Продукт 1', category_id=1, type_id=2),
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
        dtos.ItemCreateSchema(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__category_does_not_exist(self, dto, service, categories_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.add_item(new_item_info=dto)

        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.ItemCreateSchema(title='Продукт 1', category_id=1, type_id=10),
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
            dtos.ItemUpdateSchema(id=1, title='Продукт 2', category_id=3, type_id=11),
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
        assert items_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]
        assert types_repo.method_calls == [call.fetch_by_id(dto.type_id)]
        assert result == updated_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemUpdateSchema(id=100, title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__item_does_not_exist(self, dto, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.change_item(new_item_info=dto)

        assert items_repo.method_calls == [call.fetch_by_id(dto.id)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
            dtos.ItemUpdateSchema(id=1, title='Продукт 2', category_id=3, type_id=11),
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

        assert items_repo.method_calls == [call.fetch_by_id(dto.id)]
        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("existing_entity, dto", [
        (
            entities.TreatmentItem(id=1, title='Продукт 1', category_id=1, type_id=2),
            dtos.ItemUpdateSchema(id=1, title='Продукт 2', category_id=3, type_id=11),
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

        assert items_repo.method_calls == [call.fetch_by_id(dto.id)]
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
        assert items_repo.method_calls == [call.fetch_by_id(item_id),
                                           call.remove(removed_entity)]
        assert result == removed_entity

    def test__item_does_not_exist(self, service, items_repo):
        # Setup
        item_id = 1
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.delete_item(item_id=item_id)

        assert items_repo.method_calls == [call.fetch_by_id(item_id)]
