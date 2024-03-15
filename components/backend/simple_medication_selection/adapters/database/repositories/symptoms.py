from typing import Sequence, Literal

from sqlalchemy import select, asc, desc

from simple_medication_selection.application import interfaces, entities, dtos
from .base import BaseRepository


class SymptomsRepo(BaseRepository, interfaces.SymptomsRepo):
    def fetch_by_id(self, symptom_id: int) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.id == symptom_id)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  order_field: str,
                  order_direction: Literal['asc', 'desc'],
                  limit: int | None,
                  offset: int | None
                  ):
        query = (
            select(entities.Symptom)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.Symptom, order_field))
                if order_direction == 'desc'
                else asc(getattr(entities.Symptom, order_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def search_by_name(self,
                       name: str,
                       order_field: str,
                       order_direction: Literal['asc', 'desc'],
                       limit: int | None,
                       offset: int | None
                       ) -> Sequence[entities.Symptom | None]:
        query = (
            select(entities.Symptom)
            .where(entities.Symptom.name.ilike(f'%{name}%'))
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.Symptom, order_field))
                if order_direction == 'desc'
                else asc(getattr(entities.Symptom, order_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def add(self, symptom: entities.Symptom) -> entities.Symptom:
        self.session.add(symptom)
        self.session.flush()
        return symptom

    def remove(self, symptom: entities.Symptom) -> entities.Symptom:
        self.session.delete(symptom)
        self.session.flush()
        return symptom
