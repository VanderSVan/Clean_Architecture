from kombu import Connection
from sqlalchemy import create_engine

from med_sharing_system.adapters import (
    database,
    log,
    message_bus,
    settings
)
from med_sharing_system.adapters.database import TransactionContext
from med_sharing_system.adapters.message_bus.messaging_kombu import KombuPublisher
from med_sharing_system.application import services


class Settings:
    db = database.Settings()
    message_bus = message_bus.Settings()
    common_settings = settings.Settings()


class Logger:
    log.configure(
        Settings.db.LOGGING_CONFIG,
        Settings.message_bus.LOGGING_CONFIG,
    )


class DB:
    engine = create_engine(Settings.db.DATABASE_URL)

    context = TransactionContext(bind=engine, expire_on_commit=False)

    medical_books_repo = database.repositories.MedicalBooksRepo(context=context)
    patients_repo = database.repositories.PatientsRepo(context=context)


class Application:
    patient_matcher = services.PatientMatcher()


class Decorators:
    services.patient_matching_decorated_function_registry.apply_decorators(DB.context)


class MessageBus:
    connection = Connection(Settings.message_bus.RABBITMQ_URL)
    message_bus.broker_scheme.declare(connection)
    publisher = KombuPublisher(connection=connection, scheme=message_bus.broker_scheme)
    exchange_to_publishing = message_bus.EXCHANGE_TO_DELIVERY

    Application.patient_matcher.publisher = publisher
    Application.patient_matcher.targets = {
        'find_matching_patient': exchange_to_publishing
    }

    match_worker = message_bus.create_match_worker(
        connection, Application.patient_matcher
    )

    @staticmethod
    def declare_scheme():
        message_bus.broker_scheme.declare(MessageBus.connection)


if __name__ == '__main__':
    MessageBus.declare_scheme()
    MessageBus.match_worker.run()
