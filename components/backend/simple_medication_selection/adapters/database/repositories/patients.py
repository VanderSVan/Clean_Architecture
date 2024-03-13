from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class PatientsRepo(BaseRepository, interfaces.PatientsRepo):
    def fetch_by_id(self, patient_id: int) -> entities.Patient | None:
        query = select(entities.Patient).where(entities.Patient.id == patient_id)
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_nickname(self, nickname: str) -> entities.Patient | None:
        query = select(entities.Patient).where(entities.Patient.nickname == nickname)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, patient: entities.Patient) -> entities.Patient:
        self.session.add(patient)
        self.session.flush()
        return patient

    def remove(self, patient: entities.Patient) -> entities.Patient:
        self.session.delete(patient)
        self.session.flush()
        return patient
