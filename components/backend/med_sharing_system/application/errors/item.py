from .base import Error


class TreatmentItemNotFound(Error):
    message_template = 'Treatment item with id {id} not found'


class TreatmentItemAlreadyExists(Error):
    message_template = 'Treatment item with id {id} already exists'


class TreatmentItemExcludeAllFields(Error):
    message_template = "You can't exclude all columns."
    context = {'excluded_columns': list}


class TreatmentItemExcludeSortField(Error):
    message_template = ("`sort_field` should not be included in "
                        "`exclude_item_fields`. ")
    context = {'excluded_columns': list, 'sort_field': str}
