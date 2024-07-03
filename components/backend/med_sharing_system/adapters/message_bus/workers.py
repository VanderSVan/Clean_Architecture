from kombu import Connection

from med_sharing_system.application import services
from .messaging_kombu import KombuConsumer
from .scheme import broker_scheme


def create_match_worker(connection: Connection,
                        patient_matcher: services.PatientMatching
                        ) -> KombuConsumer:
    worker = KombuConsumer(connection=connection, scheme=broker_scheme)

    worker.register_function(
        patient_matcher.find_matching_patient,
        'PatientSearchQueue',
    )

    return worker
