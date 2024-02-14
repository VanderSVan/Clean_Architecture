from .base import AppError


class ItemTypeNotFound(AppError):
    msg_template = 'Item type with id {id} not found'


class ItemTypeAlreadyExists(AppError):
    msg_template = 'Item type with name {name} already exists'
