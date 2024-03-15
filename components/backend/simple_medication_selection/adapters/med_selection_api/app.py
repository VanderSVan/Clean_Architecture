import falcon

from simple_medication_selection.application import services

from .spec import spectree
from .controllers.symptoms import Symptom


def create_app(symptom: services.Symptom
               ) -> falcon.App:
    app = falcon.App()
    app.add_route('/symptoms', Symptom(symptom=symptom))
    app.add_route('/symptoms/{symptom_id}', Symptom(symptom=symptom), suffix='by_id')

    spectree.register(app)
    return app
