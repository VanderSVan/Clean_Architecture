from .base import AppError


class DiagnosisNotFound(AppError):
    msg_template = "No diagnosis with id '{id}'"


class DiagnosisAlreadyExists(AppError):
    msg_template = "Diagnosis with name '{name}' already exists"
