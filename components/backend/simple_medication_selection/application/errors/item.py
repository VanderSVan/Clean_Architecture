from .base import AppError


class TreatmentItemNotFound(AppError):
    msg_template = 'Treatment item with code {code} not found'


class TreatmentItemAlreadyExists(AppError):
    msg_template = 'Treatment item with code {code} already exists'
