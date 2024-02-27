from typing import Sequence

from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class SymptomsRepo(BaseRepository, interfaces.SymptomsRepo):
    def fetch_all(self,
                  limit: int | None,
                  offset: int | None
                  ) -> Sequence[entities.Symptom]:

        query = select(entities.Symptom).limit(limit).offset(offset)
        return self.session.execute(query).scalars().all()

    def fetch_by_id(self, symptom_id: int) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.id == symptom_id)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, symptom: entities.Symptom) -> entities.Symptom:
        self.session.add(symptom)
        self.session.flush()
        return symptom

    def remove(self, symptom: entities.Symptom) -> entities.Symptom:
        self.session.delete(symptom)
        self.session.flush()
        return symptom
