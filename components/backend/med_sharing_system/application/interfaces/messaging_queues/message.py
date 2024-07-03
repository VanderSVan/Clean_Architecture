from dataclasses import dataclass
from typing import Any


@dataclass
class QueueMessage:
    target: str
    body: Any
