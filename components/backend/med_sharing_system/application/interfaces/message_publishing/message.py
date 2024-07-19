from dataclasses import dataclass
from typing import Any


@dataclass
class QueueMessage:
    target: str  # В RabbitMQ это Exchange
    body: Any
