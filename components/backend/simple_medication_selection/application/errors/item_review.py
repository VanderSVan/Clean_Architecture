from .base import Error


class ItemReviewNotFound(Error):
    message_template = 'Item review with id {id} not found'


class ItemReviewAlreadyExists(Error):
    message_template = 'Item review with id {id} already exists'
