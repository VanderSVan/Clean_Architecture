from .base import Error


class MedicalBookNotFound(Error):
    message_template = 'Medical book with id {id} not found.'


class MedicalBookAlreadyExists(Error):
    message_template = 'Medical book with id {id} already exists.'


class MedicalBookExcludeAllFields(Error):
    message_template = "You can't exclude all columns."
    context = {'excluded_columns': list}


class MedicalBookExcludeSortField(Error):
    message_template = ("`sort_field` should not be included in "
                        "`exclude_med_book_fields`. ")
    context = {'excluded_columns': list, 'sort_field': str}

