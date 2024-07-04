import falcon
from pydantic import ValidationError

from med_sharing_system.application import services
from med_sharing_system.application.errors import Error, ErrorsList
from . import controllers
from .settings import SwaggerSettings
from .spec import setup_spectree
from .utils import error_handlers


def create_app(swagger_settings: SwaggerSettings,
               allow_origins: str | tuple[str, ...],
               api_prefix: str,
               diagnosis: services.Diagnosis,
               catalog: services.TreatmentItemCatalog,
               item_category: services.ItemCategory,
               item_review: services.ItemReview,
               item_type: services.ItemType,
               medical_book: services.MedicalBook,
               patient: services.Patient,
               symptom: services.Symptom,
               patient_matcher: services.PatientMatcher | None = None,
               ) -> falcon.App:
    cors_middleware = falcon.CORSMiddleware(allow_origins=allow_origins)
    middleware = [cors_middleware]

    app = falcon.App(middleware=middleware)

    app.add_error_handler(ValidationError, error_handlers.validation_error)
    app.add_error_handler(Error, error_handlers.app_error)
    app.add_error_handler(ErrorsList, error_handlers.app_errors_list)

    # Diagnoses
    app.add_route(f'{api_prefix}/diagnoses',
                  controllers.Diagnoses(diagnosis=diagnosis))
    app.add_route(f'{api_prefix}/diagnoses/new',
                  controllers.Diagnoses(diagnosis=diagnosis),
                  suffix='new')
    app.add_route(f'{api_prefix}/diagnoses/{{diagnosis_id}}',
                  controllers.Diagnoses(diagnosis=diagnosis),
                  suffix='by_id')

    # Patients
    app.add_route(f'{api_prefix}/patients',
                  controllers.Patients(patient=patient))
    app.add_route(f'{api_prefix}/patients/new',
                  controllers.Patients(patient=patient),
                  suffix='new')
    app.add_route(f'{api_prefix}/patients/{{patient_id}}',
                  controllers.Patients(patient=patient),
                  suffix='by_id')

    # Symptoms
    app.add_route(f'{api_prefix}/symptoms',
                  controllers.Symptoms(symptom=symptom))
    app.add_route(f'{api_prefix}/symptoms/new',
                  controllers.Symptoms(symptom=symptom),
                  suffix='new')
    app.add_route(f'{api_prefix}/symptoms/{{symptom_id}}',
                  controllers.Symptoms(symptom=symptom),
                  suffix='by_id')

    # Item Catalog
    app.add_route(f'{api_prefix}/items',
                  controllers.Catalog(catalog=catalog))
    app.add_route(f'{api_prefix}/items/new',
                  controllers.Catalog(catalog=catalog),
                  suffix='new')
    app.add_route(f'{api_prefix}/items/{{item_id}}',
                  controllers.Catalog(catalog=catalog),
                  suffix='by_id')
    app.add_route(f'{api_prefix}/items/{{item_id}}/reviews',
                  controllers.Catalog(catalog=catalog),
                  suffix='by_id_with_reviews')
    app.add_route(f'{api_prefix}/items/reviews',
                  controllers.Catalog(catalog=catalog),
                  suffix='with_reviews')

    # Item Categories
    app.add_route(f'{api_prefix}/item_categories',
                  controllers.ItemCategories(item_category=item_category))
    app.add_route(f'{api_prefix}/item_categories/new',
                  controllers.ItemCategories(item_category=item_category),
                  suffix='new')
    app.add_route(f'{api_prefix}/item_categories/{{category_id}}',
                  controllers.ItemCategories(item_category=item_category),
                  suffix='by_id')

    # Item Reviews
    app.add_route(f'{api_prefix}/item_reviews',
                  controllers.ItemReviews(item_review=item_review))
    app.add_route(f'{api_prefix}/item_reviews/{{review_id}}',
                  controllers.ItemReviews(item_review=item_review),
                  suffix='by_id')
    app.add_route(f'{api_prefix}/item_reviews/new',
                  controllers.ItemReviews(item_review=item_review),
                  suffix='new')

    # Item Types
    app.add_route(f'{api_prefix}/item_types',
                  controllers.ItemTypes(item_type=item_type))
    app.add_route(f'{api_prefix}/item_types/new',
                  controllers.ItemTypes(item_type=item_type),
                  suffix='new')
    app.add_route(f'{api_prefix}/item_types/{{type_id}}',
                  controllers.ItemTypes(item_type=item_type),
                  suffix='by_id')

    # Medical books
    app.add_route(f'{api_prefix}/medical_books',
                  controllers.MedicalBooks(medical_book=medical_book))
    app.add_route(f'{api_prefix}/medical_books/new',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='new')
    app.add_route(f'{api_prefix}/medical_books/{{med_book_id}}',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id')
    app.add_route(f'{api_prefix}/medical_books/{{med_book_id}}/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms')
    app.add_route(f'{api_prefix}/medical_books/{{med_book_id}}/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_reviews')
    app.add_route(f'{api_prefix}/medical_books/{{med_book_id}}/symptoms/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms_and_reviews')
    app.add_route(f'{api_prefix}/medical_books/{{med_book_id}}/reviews/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='by_id_with_symptoms_and_reviews')
    app.add_route(f'{api_prefix}/medical_books/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms')
    app.add_route(f'{api_prefix}/medical_books/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_reviews')
    app.add_route(f'{api_prefix}/medical_books/symptoms/reviews',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms_and_reviews')
    app.add_route(f'{api_prefix}/medical_books/reviews/symptoms',
                  controllers.MedicalBooks(medical_book=medical_book),
                  suffix='with_symptoms_and_reviews')

    # # Patient Matching
    if patient_matcher is not None:
        app.add_route(f'{api_prefix}/', controllers.Index())
        app.add_route(f'{api_prefix}/patients/match',
                      controllers.PatientMatching(patient_matcher=patient_matcher))

    if swagger_settings.ON:
        setup_spectree(
            app=app,
            title=swagger_settings.TITLE,
            path=swagger_settings.PATH,
            filename=swagger_settings.FILENAME,
            servers=swagger_settings.SERVERS,
        )

    return app
