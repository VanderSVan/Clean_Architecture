from .base import Error


class SymptomNotFound(Error):
    message_template = "No symptom with id '{id}'"


class SymptomAlreadyExists(Error):
    message_template = "Symptom with name '{name}' already exists"
