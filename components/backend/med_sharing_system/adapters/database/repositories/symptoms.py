from typing import Sequence

from sqlalchemy import select, asc, desc

from med_sharing_system.application import interfaces, entities, schemas
from .base import BaseRepository


class SymptomsRepo(BaseRepository, interfaces.SymptomsRepo):
    def fetch_by_id(self, symptom_id: int) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.id == symptom_id)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.Symptom | None:
        query = select(entities.Symptom).where(entities.Symptom.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindSymptoms
                  ) -> Sequence[entities.Symptom]:

        query = (
            select(entities.Symptom)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .order_by(
                desc(getattr(entities.Symptom, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.Symptom, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def search_by_name(self,
                       filter_params: schemas.FindSymptoms
                       ) -> Sequence[entities.Symptom | None]:

        query = (
            select(entities.Symptom)
            .where(entities.Symptom.name.ilike(f'%{filter_params.keywords}%'))
            .offset(filter_params.offset)
            .limit(filter_params.limit)
            .order_by(
                desc(getattr(entities.Symptom, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.Symptom, filter_params.sort_field))
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
