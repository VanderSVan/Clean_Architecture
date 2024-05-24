from .base import Error


class ItemCategoryNotFound(Error):
    message_template = 'Item category with id {id} not found'


class ItemCategoryAlreadyExists(Error):
    message_template = 'Item category with name {name} already exists'
