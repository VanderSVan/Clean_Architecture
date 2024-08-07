from pydantic import Field

from med_sharing_system.application import dtos


class SymptomOutput(dtos.Symptom):
    id: int | None = Field(ge=1)
    name: str | None = Field(min_length=1, max_length=255, example="Повышенная температура")