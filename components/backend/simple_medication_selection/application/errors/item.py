from .base import Error


class TreatmentItemNotFound(Error):
    message_template = 'Treatment item with id {id} not found'


class TreatmentItemAlreadyExists(Error):
    message_template = 'Treatment item with id {id} already exists'
