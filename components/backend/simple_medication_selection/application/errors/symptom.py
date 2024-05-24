from .base import Error


class SymptomNotFound(Error):
    message_template = "No symptom with id '{id}'"


class SymptomAlreadyExists(Error):
    message_template = "Symptom with name '{name}' already exists"


class SymptomExcludeAllFields(Error):
    message_template = "You can't exclude all columns."
    context = {'excluded_columns': list}
