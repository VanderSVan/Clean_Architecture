from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class DiagnosesRepo(BaseRepository, interfaces.DiagnosesRepo):
    def fetch_by_id(self, id_: int) -> entities.Diagnosis | None:
        query = select(entities.Diagnosis).where(entities.Diagnosis.id == id_)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.Diagnosis | None:
        query = select(entities.Diagnosis).where(entities.Diagnosis.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        self.session.add(diagnosis)
        self.session.flush()
        return diagnosis

    def remove(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        self.session.delete(diagnosis)
        self.session.flush()
        return diagnosis
