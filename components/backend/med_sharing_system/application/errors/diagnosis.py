from .base import Error


class DiagnosisNotFound(Error):
    message_template = "No diagnosis with id '{id}'"


class DiagnosisAlreadyExists(Error):
    message_template = "Diagnosis with name '{name}' already exists"
