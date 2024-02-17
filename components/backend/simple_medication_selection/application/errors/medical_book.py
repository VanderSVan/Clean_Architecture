from .base import AppError


class MedicalBookNotFound(AppError):
    msg_template = 'Medical book with id {id} not found.'


class MedicalBookAlreadyExists(AppError):
    msg_template = 'Medical book with id {id} already exists.'
