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
def reviews_repo() -> Mock:
    return Mock(interfaces.ItemReviewsRepo)


@pytest.fixture(scope='function')
def med_books_repo() -> Mock:
    return Mock(interfaces.MedicalBooksRepo)


@pytest.fixture(scope='function')
def symptoms_repo() -> Mock:
    return Mock(interfaces.SymptomsRepo)


@pytest.fixture(scope='function')
def diagnoses_repo() -> Mock:
    return Mock(interfaces.DiagnosesRepo)


@pytest.fixture(scope='function')
def service(items_repo,
            categories_repo,
            types_repo,
            reviews_repo,
            med_books_repo,
            symptoms_repo,
            diagnoses_repo
            ) -> services.TreatmentItemCatalog:
    return services.TreatmentItemCatalog(
        items_repo=items_repo,
        item_categories_repo=categories_repo,
        item_types_repo=types_repo,
        item_reviews_repo=reviews_repo,
        medical_books_repo=med_books_repo,
        symptoms_repo=symptoms_repo,
        diagnoses_repo=diagnoses_repo
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
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3),
             entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4),
             entities.TreatmentItem(id=4, title="Продукт 4", category_id=4, type_id=5)]
        )
    ])
    def test__find_items_by_keywords(self, keyword, result_output, service, items_repo):
        # Setup
        items_repo.fetch_by_keywords.return_value = result_output
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items(keywords="Продукт")

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_keywords("Продукт", default_limit, default_offset)
        ]
        assert result == result_output

    @pytest.mark.parametrize("result_output", [
        (
            [entities.TreatmentItem(id=1, title="Процедура 1", category_id=1, type_id=2),
             entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3),
             entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4)]
        )
    ])
    def test__find_items_without_keywords(self, result_output, service, items_repo):
        # Setup
        items_repo.fetch_all.return_value = result_output
        default_limit = 10
        default_offset = 0

        # Call
        result = service.find_items()

        # Assert
        assert items_repo.method_calls == [call.fetch_all(default_limit, default_offset)]
        assert result == result_output


class TestFindItemsByRating:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            [entities.ItemReview(
                id=1,
                item=entities.TreatmentItem(
                    id=1, title="Продукт 1", category_id=1, type_id=2
                ),
                is_helped=True,
                item_rating=8,
                item_count=3,
                usage_period=7776000
            )],
            [entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)]
        )
    ])
    def test__find_items_by_rating(self, repo_output, service_output, service,
                                   reviews_repo):
        # Setup
        reviews_repo.fetch_by_rating.return_value = repo_output
        default_limit = 10
        default_offset = 0
        min_rating = 6.5
        max_rating = 10

        # Call
        result = service.find_items_by_rating(min_rating=min_rating,
                                              max_rating=max_rating)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_by_rating(min_rating, max_rating, default_limit, default_offset)
        ]
        assert result == service_output


class TestFindItemsByHelpedStatus:
    @pytest.mark.parametrize("repo_output, service_output", [
        (
            [
                entities.ItemReview(
                    id=1,
                    item=entities.TreatmentItem(
                        id=1, title="Продукт 1", category_id=1, type_id=2
                    ),
                    is_helped=True,
                    item_rating=8,
                    item_count=3,
                    usage_period=7776000
                )
            ],
            [entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)]
        )
    ])
    def test__helped_status_is_true(self, repo_output, service_output, service,
                                    reviews_repo):
        # Setup
        reviews_repo.fetch_by_helped_status.return_value = repo_output
        default_limit = 10
        default_offset = 0
        is_helped = True

        # Call
        result = service.find_items_by_helped_status(is_helped=is_helped)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_by_helped_status(is_helped, default_limit, default_offset)
        ]
        assert result == service_output

    @pytest.mark.parametrize("repo_output, service_output", [
        (
            [
                entities.ItemReview(
                    id=2,
                    item=entities.TreatmentItem(
                        id=2, title="Продукт 2", category_id=2, type_id=3
                    ),
                    is_helped=False,
                    item_rating=2,
                    item_count=2,
                    usage_period=7776000
                )
            ],
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3)]
        )
    ])
    def test__helped_status_is_false(self, repo_output, service_output, service,
                                     reviews_repo):
        # Setup
        reviews_repo.fetch_by_helped_status.return_value = repo_output
        default_limit = 10
        default_offset = 0
        is_helped = False

        # Call
        result = service.find_items_by_helped_status(is_helped=is_helped)

        # Assert
        assert reviews_repo.method_calls == [
            call.fetch_by_helped_status(is_helped, default_limit, default_offset)
        ]
        assert result == service_output


@pytest.mark.parametrize("repo_output", [
    [
        entities.MedicalBook(
            id=1,
            title_history="Как Розацеа превратила меня в персонажа RDR2",
            history="Уот так уот",
            patient_id=1,
            diagnosis_id=1,
            symptoms=[entities.Symptom(id=1, name="Покраснение кожных покровов"),
                      entities.Symptom(id=2, name="Расширение мелких сосудов")],
            item_reviews=[
                entities.ItemReview(
                    id=1,
                    item=entities.TreatmentItem(
                        id=1, title="Продукт 1", category_id=1, type_id=2
                    ),
                    is_helped=True,
                    item_rating=6.5,
                    item_count=3,
                    usage_period=7776000
                ),
                entities.ItemReview(
                    id=2,
                    item=entities.TreatmentItem(
                        id=2, title="Продукт 2", category_id=2, type_id=3
                    ),
                    is_helped=False,
                    item_rating=7,
                    item_count=2,
                    usage_period=2592000
                )
            ]
        ),
        entities.MedicalBook(
            id=2,
            title_history="Как я справилась с Розацеа",
            history="Так и так",
            patient_id=2,
            diagnosis_id=1,
            symptoms=[entities.Symptom(id=3, name="Розовая сыпь"),
                      entities.Symptom(id=4, name="покраснение глаз")],
            item_reviews=[
                entities.ItemReview(
                    id=3,
                    item=entities.TreatmentItem(
                        id=3, title="Продукт 3", category_id=3, type_id=4
                    ),
                    is_helped=True,
                    item_rating=9.5,
                    item_count=1,
                    usage_period=7776000
                )
            ]
        )
    ]
])
class TestFindItemsBySymptomAndHelpedStatus:
    @pytest.mark.parametrize("service_output", [
        [
            entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4),
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2),
        ]
    ])
    def test__default(self, repo_output, service_output, service, med_books_repo):
        # Setup
        med_books_repo.fetch_by_symptoms.return_value = repo_output
        default_limit = 10
        default_offset = 0
        symptom_ids = [1, 2, 3, 4]

        # Call
        result = service.find_items_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids
        )

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_symptoms(symptom_ids, default_limit, default_offset)
        ]
        assert result == service_output

    @pytest.mark.parametrize("service_output", [
        [
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2),
            entities.TreatmentItem(id=3, title="Продукт 3", category_id=3, type_id=4),
        ]
    ])
    def test__asc_order(self, repo_output, service_output, service, med_books_repo):
        # Setup
        med_books_repo.fetch_by_symptoms.return_value = repo_output
        default_limit = 10
        default_offset = 0
        symptom_ids = [1, 2, 3, 4]
        order = 'asc'

        # Call
        result = service.find_items_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            order_by_rating=order
        )

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_symptoms(symptom_ids, default_limit, default_offset)
        ]
        assert result == service_output

    @pytest.mark.parametrize("service_output", [
        [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3)]
    ])
    def test__helped_status_is_false(self, repo_output, service_output, service,
                                     med_books_repo):
        # Setup
        med_books_repo.fetch_by_symptoms.return_value = repo_output
        default_limit = 10
        default_offset = 0
        symptom_ids = [1, 2, 3, 4]
        is_helped = False

        # Call
        result = service.find_items_by_symptoms_and_helped_status(
            symptom_ids=symptom_ids,
            is_helped=is_helped
        )

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_by_symptoms(symptom_ids, default_limit, default_offset)
        ]
        assert result == service_output


class TestFindItemsByDiagnosisAndHelpedStatus:
    @pytest.mark.parametrize("repo_output", [
        (
            [
                entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=3),
                entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)
            ]

        )
    ])
    def test__find_items_by_diagnosis_and_helped_status(self, repo_output, service,
                                                        med_books_repo):
        # Setup
        med_books_repo.fetch_items_by_diagnosis_and_helped_status.return_value = (
            repo_output
        )
        default_order_by_rating = 'desc'
        default_limit = 10
        default_offset = 0

        # Call
        service.find_items_by_diagnosis_and_helped_status(diagnosis_id=1)

        # Assert
        assert med_books_repo.method_calls == [
            call.fetch_items_by_diagnosis_and_helped_status(
                1, True, default_order_by_rating, default_limit, default_offset
            )
        ]


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
        default_limit = 10
        default_offset = 0
        category_id = 1

        # Call
        service.find_items_by_category(category_id=category_id)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_category(category_id, default_limit, default_offset)
        ]


class TestFindItemsByType:
    @pytest.mark.parametrize("repo_output", [
        (
            [entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=2)],
            [entities.TreatmentItem(id=2, title="Продукт 2", category_id=2, type_id=2)]
        )
    ])
    def test__find_items_by_category(self, repo_output, service, items_repo):
        # Setup
        items_repo.fetch_by_type.return_value = repo_output
        default_limit = 10
        default_offset = 0
        type_id = 1

        # Call
        service.find_items_by_type(type_id=type_id)

        # Assert
        assert items_repo.method_calls == [
            call.fetch_by_type(type_id, default_limit, default_offset)
        ]


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
    def test__create_non_existing_category(self, dto, service, categories_repo):
        # Setup
        categories_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.add_item(new_item_info=dto)

        assert categories_repo.method_calls == [call.fetch_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.ItemCreateSchema(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__create_non_existing_type(self, dto, service, categories_repo, types_repo):
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
    def test__item_is_not_exists(self, dto, service, items_repo):
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
    def test__category_is_not_exists(self, existing_entity, dto, service,
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
    def test__type_is_not_exists(self, existing_entity, dto, service, items_repo,
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
    @pytest.mark.parametrize("existing_entity, dto, removed_entity", [
        (
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=10),
            dtos.ItemDeleteSchema(id=1),
            entities.TreatmentItem(id=1, title="Продукт 1", category_id=1, type_id=10),
        )
    ])
    def test__delete_treatment_item(self, existing_entity, dto, removed_entity, service,
                                    items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = existing_entity
        items_repo.remove.return_value = removed_entity

        # Call
        result = service.delete_item(item_info=dto)

        # Assert
        assert items_repo.method_calls == [call.fetch_by_id(dto.id),
                                           call.remove(removed_entity)]
        assert result == removed_entity

    @pytest.mark.parametrize("dto", [
        dtos.ItemDeleteSchema(id=1)
    ])
    def test__item_is_not_exists(self, dto, service, items_repo):
        # Setup
        items_repo.fetch_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.delete_item(item_info=dto)

        assert items_repo.method_calls == [call.fetch_by_id(dto.id)]
