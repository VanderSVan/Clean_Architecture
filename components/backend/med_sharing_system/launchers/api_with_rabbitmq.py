from kombu import Connection
from sqlalchemy import create_engine

from med_sharing_system.adapters import med_sharing_api, database, log, message_bus
from med_sharing_system.adapters.database import TransactionContext
from med_sharing_system.adapters.message_bus.messaging_kombu import (
    KombuPublisher
)
from med_sharing_system.application import services


class Settings:
    db = database.Settings()
    api = med_sharing_api.Settings()
    message_bus = message_bus.Settings()


class Logger:
    log.configure(Settings.db.LOGGING_CONFIG,
                  Settings.api.LOGGING_CONFIG,
                  Settings.message_bus.LOGGING_CONFIG)


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


class MessageBus:
    connection = Connection(Settings.message_bus.RABBITMQ_URL)
    message_bus.broker_scheme.declare(connection)
    exchange_to_publish = message_bus.EXCHANGE_TO_MATCHING

    publisher = KombuPublisher(connection=connection, scheme=message_bus.broker_scheme)


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
    patient_matcher = services.PatientMatcher(
        publisher=MessageBus.publisher,
        targets={'publish_request_for_search_patients': MessageBus.exchange_to_publish}
    )


class Decorators:
    services.diagnosis_decorated_function_registry.apply_decorators(DB.context)
    services.item_catalog_decorated_function_registry.apply_decorators(DB.context)
    services.item_category_decorated_function_registry.apply_decorators(DB.context)
    services.item_review_decorated_function_registry.apply_decorators(DB.context)
    services.item_type_decorated_function_registry.apply_decorators(DB.context)
    services.medical_book_decorated_function_registry.apply_decorators(DB.context)
    services.patient_decorated_function_registry.apply_decorators(DB.context)
    services.symptom_decorated_function_registry.apply_decorators(DB.context)
    services.patient_matching_decorated_function_registry.apply_decorators(DB.context)


app = med_sharing_api.create_app(swagger_settings=Settings.api.SWAGGER,
                                 allow_origins=Settings.api.ALLOW_ORIGINS,
                                 api_prefix=Settings.api.API_PREFIX,
                                 diagnosis=Application.diagnosis,
                                 patient_matcher=Application.patient_matcher,
                                 patient=Application.patient,
                                 symptom=Application.symptom,
                                 item_review=Application.item_review,
                                 catalog=Application.item_catalog,
                                 item_category=Application.item_category,
                                 item_type=Application.item_type,
                                 medical_book=Application.medical_book)
