from kombu import Connection
from sqlalchemy import create_engine

from simple_medication_selection.adapters.database import TransactionContext

from simple_medication_selection.adapters import (
    database,
    log,
    message_bus,
    settings
)
from simple_medication_selection.application import services


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
    patient_matching = services.PatientMatching()


class Decorators:
    services.patient_matching_decorated_function_registry.apply_decorators(DB.context)


class MessageBus:
    connection = Connection(Settings.message_bus.RABBITMQ_URL)
    consumer = message_bus.create_consumer(connection, Application.patient_matching)

    @staticmethod
    def declare_scheme():
        message_bus.broker_scheme.declare(MessageBus.connection)


if __name__ == '__main__':
    MessageBus.declare_scheme()
    MessageBus.consumer.run()
