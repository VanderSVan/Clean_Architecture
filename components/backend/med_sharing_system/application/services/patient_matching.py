import random
import time
from typing import TypedDict

from med_sharing_system.application import interfaces, dtos, errors
from med_sharing_system.application.interfaces.messaging_queues import QueueMessage
from med_sharing_system.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class PublicationTargets(TypedDict, total=False):
    """
    Названия мест куда необходимо опубликовать сообщение.
    Как правило, это название Exchange в RabbitMQ.
    """
    publish_request_for_search_patients: str
    find_matching_patient: str


class PatientMatcher:
    def __init__(self,
                 publisher: interfaces.Publisher | None = None,
                 targets: PublicationTargets | None = None,
                 message_deliverer: interfaces.MessageSender | None = None,
                 ) -> None:
        self.publisher = publisher
        self.message_deliverer = message_deliverer
        self.targets = targets

    def publish_request_for_search_patients(self, client_id: str) -> None:
        if not self.publisher:
            raise errors.PublisherError

        if not self.targets.get('publish_request_for_search_patients'):
            raise errors.TargetNamesError

        with self.publisher:
            self.publisher.plan(
                QueueMessage(
                    self.targets['publish_request_for_search_patients'],
                    {'client_id': client_id, 'symptoms': 1}
                )
            )

    @register_method
    def find_matching_patient(self, client_id: str, symptoms: int) -> int:
        # Имитация сложной работы
        time.sleep(5)
        found_patients = random.randint(1, 10)

        if self.publisher:
            if not self.targets or not self.targets.get('find_matching_patient'):
                raise errors.TargetNamesError

            with self.publisher:
                self.publisher.plan(
                    QueueMessage(
                        self.targets['find_matching_patient'],
                        {'client_id': client_id,
                         'found_patients': found_patients}
                    )
                )
        return found_patients

    @register_method
    def send_message_to_client(self, client_id: str, found_patients: int) -> str:
        if self.message_deliverer:
            message = dtos.Message(
                target=client_id,
                title=f"Found similar patients",
                body=f"Found {found_patients} similar patients"
            )
            self.message_deliverer.send(message)
        return f"Found {found_patients} similar patients"
