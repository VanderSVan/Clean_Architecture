import falcon

from pydantic import ValidationError

from simple_medication_selection.application import services
from simple_medication_selection.application.errors import (
    Error, ErrorsList
)
from .utils import error_handlers
from .spec import spectree
from .controllers.symptoms import Symptom


def create_app(symptom: services.Symptom
               ) -> falcon.App:
    app = falcon.App()
    app.add_error_handler(ValidationError, error_handlers.validation_error)
    app.add_error_handler(Error, error_handlers.app_error)
    app.add_error_handler(ErrorsList, error_handlers.app_errors_list)
    app.add_route('/symptoms', Symptom(symptom=symptom))
    app.add_route('/symptoms/{symptom_id}', Symptom(symptom=symptom), suffix='by_id')

    spectree.register(app)
    return app
