from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function')
def treatment_items_repo() -> Mock:
    return Mock(interfaces.TreatmentItemsRepo)


@pytest.fixture(scope='function')
def item_categories_repo() -> Mock:
    return Mock(interfaces.ItemCategoriesRepo)


@pytest.fixture(scope='function')
def item_types_repo() -> Mock:
    return Mock(interfaces.ItemTypesRepo)


@pytest.fixture(scope='function')
def service(treatment_items_repo, item_categories_repo,
            item_types_repo) -> services.TreatmentItem:
    return services.TreatmentItem(
        treatment_items_repo=treatment_items_repo,
        item_categories_repo=item_categories_repo,
        item_types_repo=item_types_repo
    )


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------

class TestGet:
    @pytest.mark.parametrize("entity", [
        entities.TreatmentItem(code="Продукт 1-2-3",
                               title="Продукт 1",
                               category_id=2,
                               type_id=3)
    ])
    def test__get_existing_treatment_item(self, entity, service, treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entity

        # Call
        result = service.get(treatment_item_code='Продукт 1-2-3')

        # Assert
        assert treatment_items_repo.method_calls == [call.get_by_code('Продукт 1-2-3')]
        assert result == entity

    def test__get_non_existing_treatment_item(self, service, treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.get(treatment_item_code="Продукт 1-1-1")

        assert treatment_items_repo.method_calls == [call.get_by_code("Продукт 1-1-1")]


class TestCreate:
    @pytest.mark.parametrize("dto, saved_entity", [
        (
            dtos.TreatmentItemCreateSchema(title='Продукт 1', category_id=1, type_id=2),
            entities.TreatmentItem(title='Продукт 1', category_id=1, type_id=2),
        )
    ])
    def test__create_new_treatment_item(self,
                                        dto,
                                        saved_entity,
                                        service,
                                        treatment_items_repo,
                                        item_categories_repo,
                                        item_types_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None
        item_categories_repo.get_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        item_types_repo.get_by_id.return_value = entities.ItemType(id=2, name='Сыворотка')
        treatment_items_repo.add.return_value = saved_entity

        # Call
        result = service.create(new_treatment_item_info=dto)

        # Assert
        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code),
                                                     call.add(saved_entity)]
        assert item_categories_repo.method_calls == [call.get_by_id(dto.category_id)]
        assert item_types_repo.method_calls == [call.get_by_id(dto.type_id)]
        assert result == saved_entity

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemCreateSchema(title='Продукт 1', category_id=1, type_id=1),
    ])
    def test__create_existing_treatment_item(self, dto, service, treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entities.TreatmentItem(
            code="Продукт 1-1-1", title="Продукт 1", category_id=1, type_id=1
        )

        # Call and Assert
        with pytest.raises(errors.TreatmentItemAlreadyExists):
            service.create(new_treatment_item_info=dto)

        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code)]

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemCreateSchema(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__create_non_existing_category(self,
                                           dto,
                                           service,
                                           treatment_items_repo,
                                           item_categories_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None
        item_categories_repo.get_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.create(new_treatment_item_info=dto)

        assert item_categories_repo.method_calls == [call.get_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemCreateSchema(title='Продукт 1', category_id=1, type_id=10),
    ])
    def test__create_non_existing_type(self,
                                       dto,
                                       service,
                                       treatment_items_repo,
                                       item_types_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None
        item_types_repo.get_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.create(new_treatment_item_info=dto)

        assert item_types_repo.method_calls == [call.get_by_id(dto.type_id)]


class TestUpdate:
    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemUpdateSchema(code="Продукт 2-3-11",
                                       title='Продукт 2',
                                       category_id=3,
                                       type_id=11)
    ])
    def test__update_treatment_item(self,
                                    dto,
                                    service,
                                    treatment_items_repo,
                                    item_categories_repo,
                                    item_types_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entities.TreatmentItem(
            code="Продукт 1-1-1", title="Продукт 1", category_id=1, type_id=1
        )
        item_categories_repo.get_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        item_types_repo.get_by_id.return_value = entities.ItemType(id=10, name='Крем')

        # Call
        result = service.update(new_treatment_item_info=dto)

        # Assert
        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code)]
        assert item_categories_repo.method_calls == [call.get_by_id(dto.category_id)]
        assert item_types_repo.method_calls == [call.get_by_id(dto.type_id)]
        assert result == entities.TreatmentItem(code="Продукт 2-3-11",
                                                title="Продукт 2",
                                                category_id=3,
                                                type_id=11)

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemUpdateSchema(code="Продукт 1-1-1",
                                       title='Продукт 1',
                                       category_id=1,
                                       type_id=10),
    ])
    def test__update_non_existing_treatment_item(self,
                                                 dto,
                                                 service,
                                                 treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.update(new_treatment_item_info=dto)

        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code)]

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemUpdateSchema(code="Продукт 1-1-1",
                                       title='Продукт 1',
                                       category_id=1,
                                       type_id=10),
    ])
    def test__update_non_existing_category(self,
                                           dto,
                                           service,
                                           treatment_items_repo,
                                           item_categories_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entities.TreatmentItem(
            code="Продукт 1-1-1", title="Продукт 1", category_id=1, type_id=10
        )
        item_categories_repo.get_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemCategoryNotFound):
            service.update(new_treatment_item_info=dto)

        assert item_categories_repo.method_calls == [call.get_by_id(dto.category_id)]

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemUpdateSchema(code="Продукт 1-1-1",
                                       title='Продукт 1',
                                       category_id=1,
                                       type_id=10),
    ])
    def test_update_non_existing_type(self,
                                      dto,
                                      service,
                                      treatment_items_repo,
                                      item_categories_repo,
                                      item_types_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entities.TreatmentItem(
            code="Продукт 1-1-1", title="Продукт 1", category_id=1, type_id=10
        )
        item_categories_repo.get_by_id.return_value = (
            entities.ItemCategory(id=1, name='Аптечные продукты')
        )
        item_types_repo.get_by_id.return_value = None

        # Call and Assert
        with pytest.raises(errors.ItemTypeNotFound):
            service.update(new_treatment_item_info=dto)

        assert item_types_repo.method_calls == [call.get_by_id(dto.type_id)]


class TestDelete:
    @pytest.mark.parametrize("entity_to_delete, dto", [
        (
            entities.TreatmentItem(code="Продукт 1-1-1",
                                   title="Продукт 1",
                                   category_id=1,
                                   type_id=10),
            dtos.TreatmentItemDeleteSchema(code="Продукт 1-1-1")
        )
    ])
    def test__delete_treatment_item(self,
                                    entity_to_delete,
                                    dto,
                                    service,
                                    treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = entity_to_delete

        # Call
        service.delete(treatment_item_info=dto)

        # Assert
        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code),
                                                     call.remove(entity_to_delete)]

    @pytest.mark.parametrize("dto", [
        dtos.TreatmentItemDeleteSchema(code="Продукт 1-1-1"),
    ])
    def test__delete_non_existing_treatment_item(self,
                                                 dto,
                                                 service,
                                                 treatment_items_repo):
        # Setup
        treatment_items_repo.get_by_code.return_value = None

        # Call and Assert
        with pytest.raises(errors.TreatmentItemNotFound):
            service.delete(treatment_item_info=dto)

        assert treatment_items_repo.method_calls == [call.get_by_code(dto.code)]
