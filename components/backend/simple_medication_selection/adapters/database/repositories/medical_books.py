from typing import Sequence

from sqlalchemy import select, desc, Select, asc, func
from sqlalchemy.orm import joinedload, subqueryload

from simple_medication_selection.application import interfaces, entities, dtos, schemas
from simple_medication_selection.adapters.database.repositories.base import BaseRepository


class MedicalBooksRepo(BaseRepository, interfaces.MedicalBooksRepo):
    def fetch_by_id(self, med_book_id: int) -> dtos.MedicalBook | None:
        query: Select = (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.id == med_book_id)
        )

        result = self.session.execute(query).scalar()
        return dtos.MedicalBook.from_orm(result) if result else None

    def fetch_by_id_with_symptoms(self,
                                  med_book_id: int
                                  ) -> dtos.MedicalBookWithSymptoms | None:
        query = (
            select(entities.MedicalBook)
            .options(subqueryload(entities.MedicalBook.symptoms))
            .where(entities.MedicalBook.id == med_book_id)
        )

        result = self.session.execute(query).scalar()
        return dtos.MedicalBookWithSymptoms.from_orm(result) if result else None

    def fetch_by_id_with_reviews(self,
                                 med_book_id: int
                                 ) -> dtos.MedicalBookWithItemReviews | None:
        query = (
            select(entities.MedicalBook)
            .options(subqueryload(entities.MedicalBook.item_reviews))
            .where(entities.MedicalBook.id == med_book_id)
        )

        result = self.session.execute(query).scalar()
        return dtos.MedicalBookWithItemReviews.from_orm(result) if result else None

    def fetch_by_id_with_symptoms_and_reviews(self,
                                              med_book_id: int
                                              ) -> entities.MedicalBook | None:
        query = (
            select(entities.MedicalBook)
            .options(subqueryload(entities.MedicalBook.symptoms))
            .options(subqueryload(entities.MedicalBook.item_reviews))
            .where(entities.MedicalBook.id == med_book_id)
        )

        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindMedicalBooks
                  ) -> list[dtos.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )

        result = self.session.execute(query).scalars()
        return [dtos.MedicalBook.from_orm(row) for row in result]

    def fetch_by_symptoms(self,
                          filter_params: schemas.FindMedicalBooks
                          ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(desc(getattr(entities.MedicalBook, filter_params.sort_field))
                      if filter_params.sort_direction == 'desc'
                      else asc(getattr(entities.MedicalBook, filter_params.sort_field)))
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_matching_all_symptoms(self,
                                       filter_params: schemas.FindMedicalBooks
                                       ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_diagnosis(self,
                           filter_params: schemas.FindMedicalBooks
                           ) -> list[dtos.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBook.from_orm(row) for row in result]

    def fetch_by_diagnosis_and_symptoms(self,
                                        filter_params: schemas.FindMedicalBooks
                                        ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_helped_status(self,
                               filter_params: schemas.FindMedicalBooks
                               ) -> list[dtos.MedicalBookWithItemReviews | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithItemReviews.from_orm(row) for row in result]

    def fetch_by_helped_status_and_symptoms(self,
                                            filter_params: schemas.FindMedicalBooks
                                            ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).scalars().unique().all()

    def fetch_by_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).scalars().unique().all()

    def fetch_by_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[dtos.MedicalBookWithItemReviews | None]:

        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        result = self.session.execute(query).scalars().unique()
        return [dtos.MedicalBookWithItemReviews.from_orm(row) for row in result]

    def fetch_by_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:

        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).scalars().unique().all()

    def fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:

        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).scalars().unique().all()

    def fetch_by_patient(self,
                         filter_params: schemas.FindPatientMedicalBooks
                         ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.patient_id == filter_params.patient_id)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )

        result = self.session.execute(query).scalars()
        return [dtos.MedicalBook.from_orm(row) for row in result]

    def fetch_by_patient_and_symptoms(self,
                                      filter_params: schemas.FindPatientMedicalBooks,
                                      ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_patient_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_patient_and_helped_status(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithItemReviews | None]:
        query = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithItemReviews.from_orm(row) for row in result]

    def fetch_by_patient_helped_status_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        query = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews),
                     joinedload(entities.MedicalBook.symptoms))
        )

        return self.session.execute(query).unique().scalars().all()

    def fetch_by_patient_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms),
                     joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).unique().scalars().all()

    def fetch_by_patient_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithItemReviews | None]:
        query = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithItemReviews.from_orm(row) for row in result]

    def fetch_by_patient_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        query = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.item_reviews),
                     joinedload(entities.MedicalBook.symptoms))
        )

        return self.session.execute(query).unique().scalars().all()

    def fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:

        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms),
                     joinedload(entities.MedicalBook.item_reviews))
        )

        return self.session.execute(query).unique().scalars().all()

    def fetch_by_patient_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_patient_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .options(joinedload(entities.MedicalBook.symptoms))
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBookWithSymptoms.from_orm(row) for row in result]

    def fetch_by_patient_and_diagnosis(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBook | None]:
        query: Select = (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
            .limit(filter_params.limit)
            .offset(filter_params.offset)
        )

        result = self.session.execute(query).unique().scalars()
        return [dtos.MedicalBook.from_orm(row) for row in result]

    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.add(med_book)
        self.session.flush()
        return med_book

    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.delete(med_book)
        self.session.flush()
        return med_book
