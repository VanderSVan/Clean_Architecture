from sqlalchemy import create_engine

from med_sharing_system.adapters import api, database, log
from med_sharing_system.adapters.database import TransactionContext
from med_sharing_system.application import services


class Settings:
    db = database.Settings()
    api = api.Settings()


class Logger:
    log.configure(Settings.db.LOGGING_CONFIG, Settings.api.LOGGING_CONFIG)


class DB:
    engine = create_engine(Settings.db.DATABASE_URL)

    context = TransactionContext(bind=engine, expire_on_commit=False)

    diagnoses_repo = database.repositories.DiagnosesRepo(context=context)
    item_catalog_repo = database.repositories.TreatmentItemsRepo(context=context)
    item_categories_repo = database.repositories.ItemCategoriesRepo(context=context)
    item_reviews_repo = database.repositories.ItemReviewsRepo(context=context)
    item_types_repo = database.repositories.ItemTypesRepo(context=context)
    medical_books_repo = database.repositories.MedicalBooksRepo(context=context)
    patients_repo = database.repositories.PatientsRepo(context=context)
    symptoms_repo = database.repositories.SymptomsRepo(context=context)


class Application:
    diagnosis = services.Diagnosis(diagnoses_repo=DB.diagnoses_repo)
    item_catalog = services.TreatmentItemCatalog(
        items_repo=DB.item_catalog_repo,
        item_categories_repo=DB.item_categories_repo,
        item_types_repo=DB.item_types_repo,
        item_reviews_repo=DB.item_reviews_repo
    )
    item_category = services.ItemCategory(categories_repo=DB.item_categories_repo)
    item_review = services.ItemReview(item_reviews_repo=DB.item_reviews_repo,
                                      items_repo=DB.item_catalog_repo)
    item_type = services.ItemType(types_repo=DB.item_types_repo)
    medical_book = services.MedicalBook(
        medical_books_repo=DB.medical_books_repo,
        patients_repo=DB.patients_repo,
        diagnoses_repo=DB.diagnoses_repo,
        symptoms_repo=DB.symptoms_repo,
        reviews_repo=DB.item_reviews_repo
    )
    patient = services.Patient(patients_repo=DB.patients_repo,
                               medical_books_repo=DB.medical_books_repo)
    symptom = services.Symptom(symptoms_repo=DB.symptoms_repo)


class Decorators:
    services.diagnosis_decorated_function_registry.apply_decorators(DB.context)
    services.item_catalog_decorated_function_registry.apply_decorators(DB.context)
    services.item_category_decorated_function_registry.apply_decorators(DB.context)
    services.item_review_decorated_function_registry.apply_decorators(DB.context)
    services.item_type_decorated_function_registry.apply_decorators(DB.context)
    services.medical_book_decorated_function_registry.apply_decorators(DB.context)
    services.patient_decorated_function_registry.apply_decorators(DB.context)
    services.symptom_decorated_function_registry.apply_decorators(DB.context)


app = api.create_app(swagger_settings=Settings.api.SWAGGER,
                     allow_origins=Settings.api.ALLOW_ORIGINS,
                     api_prefix=Settings.api.API_PREFIX,
                     diagnosis=Application.diagnosis,
                     patient=Application.patient,
                     symptom=Application.symptom,
                     item_review=Application.item_review,
                     catalog=Application.item_catalog,
                     item_category=Application.item_category,
                     item_type=Application.item_type,
                     medical_book=Application.medical_book)

if __name__ == '__main__':
    import logging
    from wsgiref import simple_server

    logger = logging.getLogger('wsgi')

    httpd = simple_server.make_server('localhost', 8000, app)
    logger.info('Serving on port 8000...')
    httpd.serve_forever()
