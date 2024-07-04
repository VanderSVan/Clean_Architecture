from kombu import Connection

from med_sharing_system.application import services
from .messaging_kombu import KombuConsumer
from .scheme import broker_scheme


def create_delivery_consumer(connection: Connection,
                             patient_matcher: services.PatientMatcher
                             ) -> KombuConsumer:
    consumer = KombuConsumer(connection=connection,
                             scheme=broker_scheme,
                             prefetch_count=1)

    consumer.register_function(
        patient_matcher.send_message_to_client,
        'PatientsDeliveryQueue',
    )

    return consumer
