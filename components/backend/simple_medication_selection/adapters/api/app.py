import falcon

from pydantic import ValidationError

from simple_medication_selection.application import services
from simple_medication_selection.application.errors import (
    Error, ErrorsList
)
from .utils import error_handlers
from .spec import spectree
from . import controllers


def create_app(symptom: services.Symptom,
               catalog: services.TreatmentItemCatalog
               ) -> falcon.App:
    app = falcon.App()

    app.add_error_handler(ValidationError, error_handlers.validation_error)
    app.add_error_handler(Error, error_handlers.app_error)
    app.add_error_handler(ErrorsList, error_handlers.app_errors_list)

    app.add_route('/symptoms', controllers.Symptoms(symptom=symptom))
    app.add_route('/symptoms/new', controllers.Symptoms(symptom=symptom),
                  suffix='new')
    app.add_route('/symptoms/{symptom_id}', controllers.Symptoms(symptom=symptom),
                  suffix='by_id')

    app.add_route('/items', controllers.Catalog(catalog=catalog))
    app.add_route('/items/new', controllers.Catalog(catalog=catalog),
                  suffix='new')
    app.add_route('/items/{item_id}', controllers.Catalog(catalog=catalog),
                  suffix='by_id')

    app.add_route('/items/{item_id}/reviews', controllers.Catalog(catalog=catalog),
                  suffix='by_id_with_reviews')
    app.add_route('/items/reviews', controllers.Catalog(catalog=catalog),
                  suffix='with_reviews')

    spectree.register(app)
    return app
