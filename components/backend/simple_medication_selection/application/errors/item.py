from .base import AppError


class TreatmentItemNotFound(AppError):
    msg_template = 'Treatment item with id {id} not found'


class TreatmentItemAlreadyExists(AppError):
    msg_template = 'Treatment item with id {id} already exists'
