from .base import Error


class ItemReviewNotFound(Error):
    message_template = 'Item review with id {id} not found'


class ItemReviewAlreadyExists(Error):
    message_template = 'Item review with id {id} already exists'


class ItemReviewExcludeAllFields(Error):
    message_template = "You can't exclude all columns."
    context = {'excluded_columns': list}
