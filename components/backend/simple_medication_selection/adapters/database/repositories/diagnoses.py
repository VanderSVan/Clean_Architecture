from typing import Sequence

from sqlalchemy import select, asc, desc

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class DiagnosesRepo(BaseRepository, interfaces.DiagnosesRepo):
    def fetch_by_id(self, id_: int) -> entities.Diagnosis | None:
        query = select(entities.Diagnosis).where(entities.Diagnosis.id == id_)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.Diagnosis | None:
        query = select(entities.Diagnosis).where(entities.Diagnosis.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindDiagnoses
                  ) -> Sequence[entities.Diagnosis | None]:
        query = (
            select(entities.Diagnosis)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .order_by(
                desc(getattr(entities.Diagnosis, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.Diagnosis, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def search_by_name(self,
                       filter_params: schemas.FindDiagnoses
                       ) -> Sequence[entities.Diagnosis | None]:
        query = (
            select(entities.Diagnosis)
            .where(entities.Diagnosis.name.ilike(f'%{filter_params.keywords}%'))
            .offset(filter_params.offset)
            .limit(filter_params.limit)
            .order_by(
                desc(getattr(entities.Diagnosis, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.Diagnosis, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def add(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        self.session.add(diagnosis)
        self.session.flush()
        return diagnosis

    def remove(self, diagnosis: entities.Diagnosis) -> entities.Diagnosis:
        self.session.delete(diagnosis)
        self.session.flush()
        return diagnosis
