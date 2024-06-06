from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    target: str
    body: Any
