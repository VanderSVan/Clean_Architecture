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
               catalog: services.TreatmentItemCatalog,
               medical_book: services.MedicalBook
               ) -> falcon.App:
    app = falcon.App()

    app.add_error_handler(ValidationError, error_handlers.validation_error)
    app.add_error_handler(Error, error_handlers.app_error)
    app.add_error_handler(ErrorsList, error_handlers.app_errors_list)

    # Symptoms
    app.add_route('/symptoms', controllers.Symptoms(symptom=symptom))
    app.add_route('/symptoms/new', controllers.Symptoms(symptom=symptom),
                  suffix='new')
    app.add_route('/symptoms/{symptom_id}', controllers.Symptoms(symptom=symptom),
                  suffix='by_id')

    # Catalog
    app.add_route('/items', controllers.Catalog(catalog=catalog))
    app.add_route('/items/new', controllers.Catalog(catalog=catalog),
                  suffix='new')
    app.add_route('/items/{item_id}', controllers.Catalog(catalog=catalog),
                  suffix='by_id')
    app.add_route('/items/{item_id}/reviews', controllers.Catalog(catalog=catalog),
                  suffix='by_id_with_reviews')
    app.add_route('/items/reviews', controllers.Catalog(catalog=catalog),
                  suffix='with_reviews')

    # Medical books
    app.add_route('/medical_books',
                  controllers.MedicalBooks(medical_book=medical_book))
    app.add_route('/medical_books/new',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='new')
    app.add_route('/medical_books/{med_book_id}',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id')
    app.add_route('/medical_books/{med_book_id}/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms')
    app.add_route('/medical_books/{med_book_id}/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_reviews')
    app.add_route('/medical_books/{med_book_id}/symptoms/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms_and_reviews')
    app.add_route('/medical_books/{med_book_id}/reviews/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms_and_reviews')
    app.add_route('/medical_books/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms')
    app.add_route('/medical_books/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_reviews')
    app.add_route('/medical_books/symptoms/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms_and_reviews')
    app.add_route('/medical_books/reviews/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms_and_reviews')

    spectree.register(app)
    return app
