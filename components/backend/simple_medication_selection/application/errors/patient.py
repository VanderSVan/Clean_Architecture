from .base import AppError


class PatientNotFound(AppError):
    msg_template = 'Patient with id {id} not found'


class PatientAlreadyExists(AppError):
    msg_template = 'Patient with nickname {nickname} already exists'
