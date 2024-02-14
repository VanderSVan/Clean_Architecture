from .base import AppError


class SymptomNotFound(AppError):
    msg_template = "No symptom with id '{id}'"


class SymptomAlreadyExists(AppError):
    msg_template = "Symptom with name '{name}' already exists"
