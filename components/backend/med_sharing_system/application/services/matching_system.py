import random
import time

from med_sharing_system.application import interfaces, dtos
from med_sharing_system.application.interfaces.messaging_queues import QueueMessage
from med_sharing_system.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class PatientMatching:
    def __init__(self,
                 publisher: interfaces.Publisher | None = None,
                 message_deliverer: interfaces.MessageSender | None = None,
                 ) -> None:
        self.publisher = publisher
        self.message_deliverer = message_deliverer

    def publish_request_for_search_patients(self, client_id: str) -> None:
        with self.publisher:
            self.publisher.plan(
                QueueMessage(
                    'PatientMatching',
                    {'client_id': client_id, 'symptoms': 1}
                )
            )

    @register_method
    def find_matching_patient(self, client_id: str, symptoms: int) -> int:
        time.sleep(3)
        found_patients = random.randint(1, 10)
        if self.publisher:
            with self.publisher:
                self.publisher.plan(
                    QueueMessage(
                        'PatientDelivery',
                        {'client_id': client_id,
                         'found_patients': found_patients}
                    )
                )
        return found_patients

    @register_method
    def send_found_patients(self, client_id: str, found_patients: int):
        if self.message_deliverer:
            message = dtos.Message(
                target=client_id,
                title=f"Found similar patients",
                body=f"Found {found_patients} similar patients"
            )
            self.message_deliverer.send(message)
        return f"Found {found_patients} similar patients"
