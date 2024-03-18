from .base import Error


class MedicalBookNotFound(Error):
    message_template = 'Medical book with id {id} not found.'


class MedicalBookAlreadyExists(Error):
    message_template = 'Medical book with id {id} already exists.'
