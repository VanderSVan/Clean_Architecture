from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


# yapf: disable
class SymptomsRepo(BaseRepository, interfaces.SymptomsRepo):
    def get_by_id(self, id_: int) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.id == id_)
        return self.session.execute(query).scalars().one_or_none()

    def get_by_name(self, name: str) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, symptom: entities.Symptom) -> None:
        self.session.add(symptom)
        self.session.flush()

    def remove(self, symptom: entities.Symptom) -> None:
        self.session.delete(symptom)
        self.session.flush()

# yapf: enable
