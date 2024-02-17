from .base import AppError


class ItemReviewNotFound(AppError):
    msg_template = 'Item review with id {id} not found'


class ItemReviewAlreadyExists(AppError):
    msg_template = 'Item review with id {id} already exists'
