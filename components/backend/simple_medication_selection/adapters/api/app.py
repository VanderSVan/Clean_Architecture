import falcon
from pydantic import ValidationError

from simple_medication_selection.application import services
from simple_medication_selection.application.errors import (
    Error, ErrorsList
)
from . import controllers
from .spec import spectree
from .utils import error_handlers


def create_app(diagnosis: services.Diagnosis,
               catalog: services.TreatmentItemCatalog,
               item_category: services.ItemCategory,
               item_review: services.ItemReview,
               medical_book: services.MedicalBook,
               patient: services.Patient,
               symptom: services.Symptom
               ) -> falcon.App:
    app = falcon.App()

    app.add_error_handler(ValidationError, error_handlers.validation_error)
    app.add_error_handler(Error, error_handlers.app_error)
    app.add_error_handler(ErrorsList, error_handlers.app_errors_list)

    # Diagnoses
    app.add_route('/diagnoses', controllers.Diagnoses(diagnosis=diagnosis))
    app.add_route('/diagnoses/new', controllers.Diagnoses(diagnosis=diagnosis),
                  suffix='new')
    app.add_route('/diagnoses/{diagnosis_id}', controllers.Diagnoses(diagnosis=diagnosis),
                  suffix='by_id')

    # Patients
    app.add_route('/patients', controllers.Patients(patient=patient))
    app.add_route('/patients/new', controllers.Patients(patient=patient),
                  suffix='new')
    app.add_route('/patients/{patient_id}', controllers.Patients(patient=patient),
                  suffix='by_id')

    # Symptoms
    app.add_route('/symptoms', controllers.Symptoms(symptom=symptom))
    app.add_route('/symptoms/new', controllers.Symptoms(symptom=symptom),
                  suffix='new')
    app.add_route('/symptoms/{symptom_id}', controllers.Symptoms(symptom=symptom),
                  suffix='by_id')

    # Item Catalog
    app.add_route('/items', controllers.Catalog(catalog=catalog))
    app.add_route('/items/new', controllers.Catalog(catalog=catalog),
                  suffix='new')
    app.add_route('/items/{item_id}', controllers.Catalog(catalog=catalog),
                  suffix='by_id')
    app.add_route('/items/{item_id}/reviews', controllers.Catalog(catalog=catalog),
                  suffix='by_id_with_reviews')
    app.add_route('/items/reviews', controllers.Catalog(catalog=catalog),
                  suffix='with_reviews')

    # Item Categories
    app.add_route('/item_categories',
                  controllers.ItemCategories(item_category=item_category))
    app.add_route('/item_categories/new',
                  controllers.ItemCategories(item_category=item_category),
                  suffix='new')
    app.add_route('/item_categories/{category_id}',
                  controllers.ItemCategories(item_category=item_category),
                  suffix='by_id')

    # Item Reviews
    app.add_route('/item_reviews', controllers.ItemReviews(item_review=item_review))
    app.add_route('/item_reviews/{review_id}',
                  controllers.ItemReviews(item_review=item_review),
                  suffix='by_id')
    app.add_route('/item_reviews/new', controllers.ItemReviews(item_review=item_review),
                  suffix='new')

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
