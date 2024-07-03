from kombu import Connection
from sqlalchemy import create_engine

from med_sharing_system.adapters import (
    database,
    log,
    message_bus,
    settings
)
from med_sharing_system.adapters.database import TransactionContext
from med_sharing_system.adapters.message_delivery import WebsocketNotifier
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


class MessageSending:
    notifier = WebsocketNotifier(
        url='http://notification_worker:8000/api/v1/notify'
    )


class Application:
    patient_matching = services.PatientMatching(message_deliverer=MessageSending.notifier)


class Decorators:
    services.patient_matching_decorated_function_registry.apply_decorators(DB.context)


class MessageBus:
    connection = Connection(Settings.message_bus.RABBITMQ_URL)

    delivery_consumer = message_bus.create_delivery_consumer(
        connection, Application.patient_matching
    )

    @staticmethod
    def declare_scheme():
        message_bus.broker_scheme.declare(MessageBus.connection)


def run_delivery_consumer():
    MessageBus.declare_scheme()
    MessageBus.delivery_consumer.run()


if __name__ == '__main__':
    run_delivery_consumer()
