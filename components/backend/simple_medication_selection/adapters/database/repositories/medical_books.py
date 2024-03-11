from typing import Sequence

from sqlalchemy import select, and_, desc

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class MedicalBooksRepo(BaseRepository, interfaces.MedicalBooksRepo):
    def fetch_all(self,
                  limit: int | None = None,
                  offset: int | None = None
                  ) -> Sequence[entities.MedicalBook]:

        query = select(entities.MedicalBook).limit(limit).offset(offset)
        return self.session.execute(query).scalars().all()

    def fetch_by_id(self, med_book_id: int) -> entities.MedicalBook | None:
        query = (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.id == med_book_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_patient(self,
                         patient_id: int,
                         limit: int | None = None,
                         offset: int | None = None
                         ) -> Sequence[entities.MedicalBook]:
        query = (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.patient_id == patient_id)
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_symptoms(self,
                          symptom_ids: list[int],
                          limit: int | None = None,
                          offset: int | None = None
                          ) -> Sequence[entities.MedicalBook | None]:
        query = (
            select(entities.MedicalBook)
            .where(
                entities.MedicalBook.symptoms.any(entities.Symptom.id.in_(symptom_ids))
            )
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[entities.MedicalBook | None]:

        query = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .where(
                and_(
                    entities.MedicalBook.symptoms.any(
                        entities.Symptom.id.in_(symptom_ids)
                    ),
                    entities.ItemReview.is_helped == is_helped
                )
            )
            .order_by(desc(entities.MedicalBook.id))
            .limit(limit)
            .offset(offset)
            .distinct(entities.MedicalBook.id)
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        limit: int | None = None,
        offset: int | None = None
    ) -> Sequence[entities.MedicalBook | None]:

        query = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .where(
                and_(
                    entities.MedicalBook.diagnosis_id == diagnosis_id,
                    entities.ItemReview.is_helped == is_helped
                )
            )
            .order_by(desc(entities.MedicalBook.id))
            .limit(limit)
            .offset(offset)
            .distinct(entities.MedicalBook.id)
        )
        return self.session.execute(query).scalars().all()

    def add(self, medical_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.add(medical_book)
        self.session.flush()
        return medical_book

    def remove(self, medical_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.delete(medical_book)
        self.session.flush()
        return medical_book
