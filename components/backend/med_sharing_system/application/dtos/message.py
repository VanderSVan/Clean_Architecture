from pydantic import Field

from .base import DTO


class Message(DTO):
    target: str = Field(min_length=1, max_length=255)
    title: str | None = Field(min_length=1, max_length=1000)
    body: str = Field(min_length=1, max_length=5000)
