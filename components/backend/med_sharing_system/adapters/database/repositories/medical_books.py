from typing import Sequence

from sqlalchemy import select, desc, Select, asc, func
from sqlalchemy.orm import joinedload, Session

from med_sharing_system.adapters.database.repositories.base import BaseRepository
from med_sharing_system.application import interfaces, entities, schemas


class MedicalBooksRepo(BaseRepository, interfaces.MedicalBooksRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.query_collection = _MedicalBookQueryCollection()
        self.query_pagination = _MedicalBookQueryPagination()
        self.query_executor = _MedicalBookQueryExecutor(self.session)

    def fetch_by_id(self,
                    med_book_id: int,
                    *,
                    include_symptoms: bool,
                    include_reviews: bool
                    ) -> entities.MedicalBook | None:
        query: Select = self.query_collection.fetch_by_id(med_book_id)
        return self.query_executor.get_med_book(query, include_symptoms, include_reviews)

    def fetch_all(self,
                  filter_params: schemas.FindMedicalBooks,
                  *,
                  include_symptoms: bool,
                  include_reviews: bool
                  ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_all()
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_symptoms(self,
                          filter_params: schemas.FindMedicalBooks,
                          *,
                          include_symptoms: bool,
                          include_reviews: bool
                          ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_symptoms(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_matching_all_symptoms(self,
                                       filter_params: schemas.FindMedicalBooks,
                                       *,
                                       include_symptoms: bool,
                                       include_reviews: bool
                                       ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_matching_all_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_diagnosis(self,
                           filter_params: schemas.FindMedicalBooks,
                           *,
                           include_symptoms: bool,
                           include_reviews: bool
                           ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_diagnosis(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_diagnosis_and_symptoms(self,
                                        filter_params: schemas.FindMedicalBooks,
                                        *,
                                        include_symptoms: bool,
                                        include_reviews: bool
                                        ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_diagnosis_and_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_diagnosis_with_matching_all_symptoms(
                filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status(self,
                               filter_params: schemas.FindMedicalBooks,
                               *,
                               include_symptoms: bool,
                               include_reviews: bool
                               ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_helped_status(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_and_symptoms(self,
                                            filter_params: schemas.FindMedicalBooks,
                                            *,
                                            include_symptoms: bool,
                                            include_reviews: bool
                                            ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_and_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_and_diagnosis(self,
                                             filter_params: schemas.FindMedicalBooks,
                                             *,
                                             include_symptoms: bool,
                                             include_reviews: bool
                                             ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_and_diagnosis(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_diagnosis_and_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_helped_status_diagnosis_with_matching_all_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient(self,
                         filter_params: schemas.FindMedicalBooks,
                         *,
                         include_symptoms: bool,
                         include_reviews: bool
                         ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_patient(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_and_symptoms(self,
                                      filter_params: schemas.FindMedicalBooks,
                                      *,
                                      include_symptoms: bool,
                                      include_reviews: bool
                                      ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_patient_and_symptoms(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_and_helped_status(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_and_helped_status(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_helped_status_and_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_helped_status_with_matching_all_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_helped_status_and_diagnosis(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_helped_status_diagnosis_and_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_diagnosis_with_matching_all_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_diagnosis_and_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_and_diagnosis(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_items(self,
                       filter_params: schemas.FindMedicalBooks,
                       *,
                       include_symptoms: bool,
                       include_reviews: bool
                       ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_items(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_and_items(self,
                                   filter_params: schemas.FindMedicalBooks,
                                   *,
                                   include_symptoms: bool,
                                   include_reviews: bool
                                   ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_patient_and_items(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_items_and_helped_status(self,
                                         filter_params: schemas.FindMedicalBooks,
                                         *,
                                         include_symptoms: bool,
                                         include_reviews: bool
                                         ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_items_and_helped_status(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_items_and_diagnosis(self,
                                     filter_params: schemas.FindMedicalBooks,
                                     *,
                                     include_symptoms: bool,
                                     include_reviews: bool
                                     ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_items_and_diagnosis(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_items_and_symptoms(self,
                                    filter_params: schemas.FindMedicalBooks,
                                    *,
                                    include_symptoms: bool,
                                    include_reviews: bool
                                    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = self.query_collection.fetch_by_items_and_symptoms(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_items_with_matching_all_symptoms(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_diagnosis_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_helped_status_diagnosis_and_items(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_diagnosis_and_items(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_helped_status_and_items(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_helped_status_diagnosis_and_items(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_helped_status_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        query: Select = (
            self
            .query_collection
            .fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.query_executor.get_med_book_list(query,
                                                     include_symptoms,
                                                     include_reviews)

    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.add(med_book)
        self.session.flush()
        return med_book

    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        self.session.delete(med_book)
        self.session.flush()
        return med_book


class _MedicalBookQueryExecutor:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_med_book(self,
                     query: Select,
                     include_symptoms: bool,
                     include_reviews: bool
                     ) -> entities.MedicalBook | None:

        self._set_query_options(query, include_symptoms, include_reviews)
        return self.session.execute(query).scalars().unique().one_or_none()

    def get_med_book_list(self,
                          query: Select,
                          include_symptoms: bool,
                          include_reviews: bool
                          ) -> Sequence[entities.MedicalBook | None]:

        self._set_query_options(query, include_symptoms, include_reviews)
        return self.session.execute(query).scalars().unique().all()

    @staticmethod
    def _set_query_options(query: Select,
                           include_symptoms: bool,
                           include_reviews: bool
                           ) -> Select:
        if include_symptoms and include_reviews:
            return query.options(joinedload(entities.MedicalBook.symptoms),
                                 joinedload(entities.MedicalBook.item_reviews))

        if include_reviews:
            return query.options(joinedload(entities.MedicalBook.item_reviews))

        if include_symptoms:
            return query.options(joinedload(entities.MedicalBook.symptoms))

        return query


class _MedicalBookQueryPagination:
    def apply(self, query, filter_params) -> Select:
        query = self.set_order(query, filter_params)
        query = self.set_limit(query, filter_params)
        query = self.set_offset(query, filter_params)
        return query

    @staticmethod
    def set_order(query, filter_params) -> Select:
        if filter_params.sort_field is None:
            return query

        return (
            query.order_by(
                desc(getattr(entities.MedicalBook, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.MedicalBook, filter_params.sort_field))
            )
        )

    @staticmethod
    def set_limit(query, filter_params) -> Select:
        if filter_params.limit is None:
            return query

        return query.limit(filter_params.limit)

    @staticmethod
    def set_offset(query, filter_params) -> Select:
        if filter_params.offset is None:
            return query

        return query.offset(filter_params.offset)


class _MedicalBookQueryCollection:

    @staticmethod
    def fetch_by_id(med_book_id: int) -> Select:
        return (
            select(entities.MedicalBook)
            .where(entities.MedicalBook.id == med_book_id)
        )

    @staticmethod
    def fetch_all() -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
        )

    @staticmethod
    def fetch_by_symptoms(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_matching_all_symptoms(filter_params: schemas.FindMedicalBooks
                                       ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_diagnosis(filter_params: schemas.FindMedicalBooks
                           ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
        )

    @staticmethod
    def fetch_by_diagnosis_and_symptoms(filter_params: schemas.FindMedicalBooks
                                        ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_diagnosis_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_helped_status_and_symptoms(filter_params: schemas.FindMedicalBooks
                                            ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status_and_diagnosis(filter_params: schemas.FindMedicalBooks
                                             ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_helped_status_diagnosis_and_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.patient_id == filter_params.patient_id)
        )

    @staticmethod
    def fetch_by_patient_and_symptoms(filter_params: schemas.FindMedicalBooks,
                                      ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_and_helped_status(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_patient_helped_status_and_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_and_diagnosis(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_patient_helped_status_diagnosis_and_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
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
        )

    @staticmethod
    def fetch_by_patient_diagnosis_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_diagnosis_and_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_and_diagnosis(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
        )

    @staticmethod
    def fetch_by_items(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_patient_and_items(filter_params: schemas.FindMedicalBooks
                                   ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_items_and_helped_status(filter_params: schemas.FindMedicalBooks
                                         ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_items_and_diagnosis(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_items_and_symptoms(filter_params: schemas.FindMedicalBooks) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_items_with_matching_all_symptoms(filter_params: schemas.FindMedicalBooks
                                                  ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_diagnosis_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_helped_status_diagnosis_and_items(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_diagnosis_and_items(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_and_items(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_diagnosis_and_items(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )

    @staticmethod
    def fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
        filter_params: schemas.FindMedicalBooks
    ) -> Select:
        return (
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.MedicalBook.id)
            .having(func.count(entities.Symptom.id.distinct()) == len(
                filter_params.symptom_ids))
        )
