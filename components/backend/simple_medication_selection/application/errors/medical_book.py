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


class MedicalBookSymptomsIntersection(Error):
    message_template = ("`symptom_ids_to_add` and `symptom_ids_to_remove` "
                        "should not intersect. ")
    context = {'symptom_ids_to_add': list, 'symptom_ids_to_remove': list}


class MedicalBookReviewsIntersection(Error):
    message_template = ("`item_review_ids_to_add` and `item_review_ids_to_remove` "
                        "should not intersect. ")
    context = {'item_review_ids_to_add': list, 'item_review_ids_to_remove': list}

