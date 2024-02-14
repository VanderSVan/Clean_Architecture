from .base import AppError


class ItemCategoryNotFound(AppError):
    msg_template = 'Item category with id {id} not found'


class ItemCategoryAlreadyExists(AppError):
    msg_template = 'Item category with name {name} already exists'
