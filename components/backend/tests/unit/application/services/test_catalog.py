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
        assert items_repo.method_calls == [call.fetch_by_id(existing_entity.id, False)]
        assert result == existing_entity

    def test__get_non_existing_treatment_item(self, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None
        item_id = 1

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get_item(item_id=item_id)

        assert items_repo.method_calls == [call.fetch_by_id(item_id, False)]


class TestGetItemsWithReviews:
    @pytest.mark.parametrize("existing_entity", [
        entities.TreatmentItem(
            id=1, title="Продукт 1", category_id=2, type_id=3
        )
    ])
    def test__get_existing_treatment_item(self, existing_entity, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity

        # Call
        result = service.get_item_with_reviews(item_id=existing_entity.id)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(existing_entity.id, True)]
        assert result == existing_entity

    def test__get_non_existing_treatment_item(self, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None
        item_id = 1

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get_item_with_reviews(item_id=item_id)

        assert items_repo.method_calls == [call.fetch_by_id(item_id, True)]


class TestFindItems:

    @pytest.mark.parametrize("result_output", [
        [
            dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                               description='Описание 3', category_id=2, type_id=3,
                               avg_rating=8.5),
            dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                               description="Описание 1", category_id=1, type_id=2,
                               avg_rating=7.75)
        ]
    ])
    def test__with_keywords(self, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(keywords="Продукт")

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("helped_status, result_output", [
        (
            True,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                          description='Описание 3', category_id=2,
                                          type_id=3, avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                          description="Описание 1", category_id=1,
                                          type_id=2, avg_rating=7.75)
            ],
        ),
        (
            False,
            [
                dtos.TreatmentItem(id=2, title="Процедура 1", price=3000.55,
                                          description='Описание 2', category_id=2,
                                          type_id=3, avg_rating=5),
                dtos.TreatmentItem(id=1, title="Продукт 5", price=None,
                                          description="Описание 5", category_id=1,
                                          type_id=2, avg_rating=3.5)
            ],
        )
    ])
    def test__with_helped_status(self, helped_status, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_helped_status.return_value = result_output
        filter_params = schemas.FindTreatmentItems(is_helped=True)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_helped_status(filter_params, False)
        ]
        assert result == result_output

    @pytest.mark.parametrize("diagnosis_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                       description='Описание 3', category_id=2,
                                       type_id=3, avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                       description="Описание 1", category_id=1,
                                       type_id=2, avg_rating=7.75)
            ],
        )
    ])
    def test_with_diagnosis(self, diagnosis_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_diagnosis.return_value = result_output
        filter_params = schemas.FindTreatmentItems(diagnosis_id=1)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_diagnosis(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("symptom_ids, result_output", [
        (
            [1, 2, 3],
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=2,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=3,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_symptoms(self, symptom_ids, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_symptoms.return_value = result_output
        filter_params = schemas.FindTreatmentItems(symptom_ids=[1, 2, 3])

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_symptoms(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("min_rating, max_rating, result_output", [
        (
            1.5,
            9.5,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_rating(self, min_rating, max_rating, result_output, service,
                          items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(min_rating=min_rating,
                                                   max_rating=max_rating)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("min_price, max_price, result_output", [
        (
            1000,
            10000,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_price(self, min_price, max_price, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(min_price=min_price,
                                                   max_price=max_price)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("category_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=1, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_category(self, category_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(category_id=1)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("type_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=1,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=1,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_type(self, type_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(type_id=1)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("sort_field, sort_direction, result_output", [
        (
            "title",
            'asc',
            [
                dtos.TreatmentItem(id=3, title="Продукт 1", price=5000,
                                   description='Описание 1', category_id=2, type_id=1,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 3", price=7500.50,
                                   description="Описание 3", category_id=1, type_id=10,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_sort(self, sort_field, sort_direction, result_output, service,
                        items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(sort_field=sort_field,
                                                   sort_direction=sort_direction)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output

    @pytest.mark.parametrize("offset, limit, result_output", [
        (
            1,
            1,
            [dtos.TreatmentItem(id=1, title="Продукт 3", price=7500.50,
                                description="Описание 3", category_id=1, type_id=10,
                                avg_rating=7.75)]
        )
    ])
    def test__with_offset_and_limit(self, offset, limit, result_output, service,
                                    items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(offset=offset, limit=limit)

        # Call
        result = service.find_items(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, False)]
        assert result == result_output


class TestFindItemsWithReviews:

    @pytest.mark.parametrize("result_output", [
        [
            dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                               description='Описание 3', category_id=2, type_id=3,
                               avg_rating=8.5),
            dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                               description="Описание 1", category_id=1, type_id=2,
                               avg_rating=7.75)
        ]
    ])
    def test__with_keywords(self, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(keywords="Продукт")

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("helped_status, result_output", [
        (
            True,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                          description='Описание 3', category_id=2,
                                          type_id=3, avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                          description="Описание 1", category_id=1,
                                          type_id=2, avg_rating=7.75)
            ],
        ),
        (
            False,
            [
                dtos.TreatmentItem(id=2, title="Процедура 1", price=3000.55,
                                          description='Описание 2', category_id=2,
                                          type_id=3, avg_rating=5),
                dtos.TreatmentItem(id=1, title="Продукт 5", price=None,
                                          description="Описание 5", category_id=1,
                                          type_id=2, avg_rating=3.5)
            ],
        )
    ])
    def test__with_helped_status(self, helped_status, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_helped_status.return_value = result_output
        filter_params = schemas.FindTreatmentItems(is_helped=True)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_helped_status(filter_params, True)
        ]
        assert result == result_output

    @pytest.mark.parametrize("diagnosis_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                       description='Описание 3', category_id=2,
                                       type_id=3, avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                       description="Описание 1", category_id=1,
                                       type_id=2, avg_rating=7.75)
            ],
        )
    ])
    def test_with_diagnosis(self, diagnosis_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_diagnosis.return_value = result_output
        filter_params = schemas.FindTreatmentItems(diagnosis_id=1)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_diagnosis(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("symptom_ids, result_output", [
        (
            [1, 2, 3],
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=2,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=3,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_symptoms(self, symptom_ids, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_symptoms.return_value = result_output
        filter_params = schemas.FindTreatmentItems(symptom_ids=[1, 2, 3])

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_symptoms(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("min_rating, max_rating, result_output", [
        (
            1.5,
            9.5,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_rating(self, min_rating, max_rating, result_output, service,
                          items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(min_rating=min_rating,
                                                   max_rating=max_rating)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("min_price, max_price, result_output", [
        (
            1000,
            10000,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_price(self, min_price, max_price, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(min_price=min_price,
                                                   max_price=max_price)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("category_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=1, type_id=3,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=2,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_category(self, category_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(category_id=1)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("type_id, result_output", [
        (
            1,
            [
                dtos.TreatmentItem(id=3, title="Продукт 3", price=5000,
                                   description='Описание 3', category_id=2, type_id=1,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 1", price=7500.50,
                                   description="Описание 1", category_id=1, type_id=1,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_type(self, type_id, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(type_id=1)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("sort_field, sort_direction, result_output", [
        (
            "title",
            'asc',
            [
                dtos.TreatmentItem(id=3, title="Продукт 1", price=5000,
                                   description='Описание 1', category_id=2, type_id=1,
                                   avg_rating=8.5),
                dtos.TreatmentItem(id=1, title="Продукт 3", price=7500.50,
                                   description="Описание 3", category_id=1, type_id=10,
                                   avg_rating=7.75)
            ]
        )
    ])
    def test__with_sort(self, sort_field, sort_direction, result_output, service,
                        items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(sort_field=sort_field,
                                                   sort_direction=sort_direction)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output

    @pytest.mark.parametrize("offset, limit, result_output", [
        (
            1,
            1,
            [dtos.TreatmentItem(id=1, title="Продукт 3", price=7500.50,
                                description="Описание 3", category_id=1, type_id=10,
                                avg_rating=7.75)]
        )
    ])
    def test__with_offset_and_limit(self, offset, limit, result_output, service,
                                    items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        filter_params = schemas.FindTreatmentItems(offset=offset, limit=limit)

        # Call
        result = service.find_items_with_reviews(filter_params=filter_params)

        # Assert
        assert items_repo.method_calls == [call.fetch_all(filter_params, True)]
        assert result == result_output


class TestAddItem:
    @pytest.mark.parametrize("new_entity, dto, saved_entity", [
        (
            entities.TreatmentItem(title='Продукт 1', category_id=1, type_id=2),
            dtos.NewItemInfo(title='Продукт 1', category_id=1, type_id=2),
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
        dtos.NewItemInfo(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__category_does_not_exist(self, dto, service, categories_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.add_item(new_item_info=dto)

        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.NewItemInfo(title='Продукт 1', category_id=1, type_id=10),
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
            dtos.UpdatedItemInfo(id=1, title='Продукт 2', category_id=3, type_id=11),
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
        dtos.UpdatedItemInfo(id=100, title='Продукт 1', category_id=1, type_id=10),
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
            dtos.UpdatedItemInfo(id=1, title='Продукт 2', category_id=3, type_id=11),
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
            dtos.UpdatedItemInfo(id=1, title='Продукт 2', category_id=3, type_id=11),
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
