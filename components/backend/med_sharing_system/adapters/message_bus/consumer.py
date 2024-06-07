from kombu import Connection

from med_sharing_system.application import services
from .messaging_kombu import KombuConsumer
from .scheme import broker_scheme


def create_consumer(connection: Connection,
                    patient_matcher: services.PatientMatching) -> KombuConsumer:
    consumer = KombuConsumer(connection=connection, scheme=broker_scheme)

    consumer.register_function(
        patient_matcher.send_similar_patients_count,
        'PatientsMatchedQueue',
    )

    return consumer
