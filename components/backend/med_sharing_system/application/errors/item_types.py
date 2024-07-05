from .base import Error


class ItemTypeNotFound(Error):
    message_template = 'Item type with id {id} not found'


class ItemTypeAlreadyExists(Error):
    message_template = 'Item type with name {name} already exists'
