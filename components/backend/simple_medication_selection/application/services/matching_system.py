import random

import gevent

from simple_medication_selection.application.interfaces.messaging.publisher import (
    Publisher,
    Message,
)
from simple_medication_selection.application.utils import DecoratedFunctionRegistry

decorated_function_registry = DecoratedFunctionRegistry()
register_method = decorated_function_registry.register_function


class PatientMatching:
    def __init__(self, publisher: Publisher | None = None):
        self.publisher = publisher

    @register_method
    def _find_matching_patient_task(self) -> int:
        gevent.sleep(5)
        found_patients = random.randint(1, 10)
        if self.publisher:
            with self.publisher:
                self.publisher.plan(
                    Message('PatientMatching', {'found_patients': found_patients})
                )
        return found_patients

    def find_matching_patient(self) -> None:
        # Запуск задачи в фоновом режиме
        gevent.spawn(self._find_matching_patient_task)

    def send_similar_patients_count(self, found_patients: int):
        return f"Found {found_patients} similar patients"
