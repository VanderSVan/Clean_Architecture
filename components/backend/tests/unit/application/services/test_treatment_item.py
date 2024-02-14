from unittest.mock import Mock, call

import pytest
from simple_medication_selection.application import (dtos, entities, errors,
                                                     interfaces, services)


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------
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
def service(treatment_items_repo, item_categories_repo, item_types_repo) -> services.TreatmentItem:
    return services.TreatmentItem(
        treatment_items_repo=treatment_items_repo,
        item_categories_repo=item_categories_repo,
        item_types_repo=item_types_repo
    )


# ----------------------------------------------------------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("entity", [
    entities.TreatmentItem(title="Продукт 1", category_id=1, type_id=1),
])
def test__get_existing_treatment_item(entity, service, repo):
    # Setup
    repo.get_by_id.return_value = entity

    # Call
    service.get(item_category_id=entity.id)

    # Assert
    expected_calls_for_repo = [call.get_by_id(entity.id)]
    assert repo.method_calls == expected_calls_for_repo