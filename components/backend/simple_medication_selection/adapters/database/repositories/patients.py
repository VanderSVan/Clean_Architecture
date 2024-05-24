from typing import Sequence

from sqlalchemy import select, desc, asc, between, Select

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class PatientsRepo(BaseRepository, interfaces.PatientsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.query_pagination = _PatientQueryPagination()

    def fetch_by_id(self, patient_id: int) -> entities.Patient | None:
        query = select(entities.Patient).where(entities.Patient.id == patient_id)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_nickname(self, nickname: str) -> entities.Patient | None:
        query = select(entities.Patient).where(entities.Patient.nickname == nickname)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindPatients
                  ) -> Sequence[entities.Patient]:
        query: Select = select(entities.Patient).distinct()
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_gender(self,
                        filter_params: schemas.FindPatients
                        ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.gender == filter_params.gender)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_age(self,
                     filter_params: schemas.FindPatients
                     ) -> Sequence[entities.Patient]:

        query: Select = select(entities.Patient).distinct()
        query: Select = self._add_age_filter(query, filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_skin_type(self,
                           filter_params: schemas.FindPatients
                           ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.skin_type == filter_params.skin_type)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_gender_and_age(self,
                                filter_params: schemas.FindPatients
                                ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.gender == filter_params.gender)
        )
        query: Select = self._add_age_filter(query, filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_gender_and_skin_type(self,
                                      filter_params: schemas.FindPatients
                                      ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.gender == filter_params.gender,
                   entities.Patient.skin_type == filter_params.skin_type)

        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_age_and_skin_type(self,
                                   filter_params: schemas.FindPatients
                                   ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.skin_type == filter_params.skin_type)
        )
        query: Select = self._add_age_filter(query, filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_gender_age_and_skin_type(self,
                                          filter_params: schemas.FindPatients
                                          ) -> Sequence[entities.Patient]:
        query: Select = (
            select(entities.Patient)
            .distinct()
            .where(entities.Patient.gender == filter_params.gender,
                   entities.Patient.skin_type == filter_params.skin_type)
        )
        query: Select = self._add_age_filter(query, filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def add(self, patient: entities.Patient) -> entities.Patient:
        self.session.add(patient)
        self.session.flush()
        return patient

    def remove(self, patient: entities.Patient) -> entities.Patient:
        self.session.delete(patient)
        self.session.flush()
        return patient

    @staticmethod
    def _add_age_filter(query: Select, filter_params: schemas.FindPatients) -> Select:

        if filter_params.age_from is not None and filter_params.age_to is not None:
            return query.where(between(entities.Patient.age,
                                       filter_params.age_from, filter_params.age_to))

        if filter_params.age_from is not None:
            return query.where(entities.Patient.age >= filter_params.age_from)

        return query.where(entities.Patient.age <= filter_params.age_to)


class _PatientQueryPagination:
    def apply(self, query: Select, filter_params: schemas.FindPatients) -> Select:
        query = self.set_order(query, filter_params)
        query = self.set_limit(query, filter_params)
        query = self.set_offset(query, filter_params)
        return query

    @staticmethod
    def set_order(query: Select, filter_params: schemas.FindPatients) -> Select:
        if filter_params.sort_field is None:
            return query

        sort_field = getattr(entities.Patient, filter_params.sort_field)
        return (
            query.order_by(
                desc(sort_field).nullslast()
                if filter_params.sort_direction == 'desc'
                else asc(sort_field).nullslast()
            )
        )

    @staticmethod
    def set_limit(query: Select, filter_params: schemas.FindPatients) -> Select:
        if filter_params.limit is None:
            return query

        return query.limit(filter_params.limit)

    @staticmethod
    def set_offset(query: Select, filter_params: schemas.FindPatients) -> Select:
        if filter_params.offset is None:
            return query

        return query.offset(filter_params.offset)
