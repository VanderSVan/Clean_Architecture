from .base import Error


class PatientNotFound(Error):
    message_template = 'Patient with id {id} not found'


class PatientAlreadyExists(Error):
    message_template = 'Patient with nickname {nickname} already exists'
