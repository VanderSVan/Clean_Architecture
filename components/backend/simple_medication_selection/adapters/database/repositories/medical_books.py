from typing import Sequence

from sqlalchemy import select, desc

from simple_medication_selection.application import interfaces, entities, dtos
from .base import BaseRepository


class MedicalBooksRepo(BaseRepository, interfaces.MedicalBooksRepo):
    def fetch_by_id(self, med_book_id: int) -> entities.MedicalBook | None:
        query = (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.id == med_book_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_patient(self,
                         patient_id: int,
                         limit: int | None,
                         offset: int | None
                         ) -> Sequence[entities.MedicalBook | None]:
        query = (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.patient_id == patient_id)
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_symptoms_and_helped_status(self,
                                            symptom_ids: list[int],
                                            is_helped: bool,
                                            limit: int | None,
                                            offset: int | None
                                            ) -> list[dtos.MedicalBookGetSchema | None]:
        query = (
            select(
                entities.MedicalBook.id,
                entities.MedicalBook.title_history,
                entities.MedicalBook.history,
                entities.MedicalBook.patient_id,
                entities.MedicalBook.diagnosis_id,
            )
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(
                entities.MedicalBook.symptoms.any(entities.Symptom.id.in_(symptom_ids)),
                entities.ItemReview.is_helped == is_helped
            )
            .distinct(entities.MedicalBook.id)
            .limit(limit)
            .offset(offset)
            .order_by(desc(entities.MedicalBook.id))
        )

        result = self.session.execute(query).mappings()
        return [dtos.MedicalBookGetSchema(**row) for row in result]

    def fetch_by_diagnosis_and_helped_status(self,
                                             diagnosis_id: int,
                                             is_helped: bool,
                                             limit: int | None,
                                             offset: int | None
                                             ) -> list[dtos.MedicalBookGetSchema | None]:
        query = (
            select(
                entities.MedicalBook.id,
                entities.MedicalBook.title_history,
                entities.MedicalBook.history,
                entities.MedicalBook.patient_id,
                entities.MedicalBook.diagnosis_id,
            )
            .join(entities.MedicalBook.item_reviews)
            .where(
                entities.MedicalBook.diagnosis_id == diagnosis_id,
                entities.ItemReview.is_helped == is_helped
            )
            .distinct(entities.MedicalBook.id)
            .limit(limit)
            .offset(offset)
            .order_by(desc(entities.MedicalBook.id))
        )

        result = self.session.execute(query).mappings()
        return [dtos.MedicalBookGetSchema(**row) for row in result]

    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.add(med_book)
        self.session.flush()
        return med_book

    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.delete(med_book)
        self.session.flush()
        return med_book
