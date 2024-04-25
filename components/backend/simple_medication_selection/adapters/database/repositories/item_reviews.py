from typing import Sequence

from sqlalchemy import select, desc, asc, between, Select, RowMapping
from sqlalchemy.orm import InstrumentedAttribute, Session

from simple_medication_selection.application import interfaces, entities, schemas, dtos
from .base import BaseRepository


class ItemReviewsRepo(BaseRepository, interfaces.ItemReviewsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.query_collection = _ItemReviewQueryCollection()
        self.query_pagination = _ItemReviewQueriesPagination()
        self.query_executor = _ItemReviewQueryExecutor(self.session)

    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        query: Select = self.query_collection.fetch_by_id(review_id)
        return self.query_executor.fetch_review(query)

    def fetch_all(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_all()
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_by_items(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_patient(self,
                         filter_params: schemas.FindItemReviews,
                         ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:
        query: Select = self.query_collection.fetch_by_patient(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_patient_reviews_by_item(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_patient_reviews_by_item(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_rating(self,
                        filter_params: schemas.FindItemReviews,
                        ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:
        query: Select = self.query_collection.fetch_by_rating(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_helped_status(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_by_helped_status(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_and_patient(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_by_items_and_patient(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_and_helped_status(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_items_and_helped_status(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_by_items_and_rating(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_patient_and_helped_status(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_patient_and_helped_status(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_patient_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = self.query_collection.fetch_by_patient_and_rating(filter_params)
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_helped_status_and_rating(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_patient_and_helped_status(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_items_patient_and_helped_status(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_patient_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_items_patient_and_rating(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:

        query: Select = (
            self.query_collection.fetch_by_items_helped_status_and_rating(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_patient_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:
        query: Select = (
            self.query_collection.fetch_by_patient_helped_status_and_rating(filter_params)
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def fetch_by_items_patient_helped_status_and_rating(
        self,
        filter_params: schemas.FindItemReviews,
    ) -> Sequence[entities.ItemReview | dtos.ItemReview | None]:
        query: Select = (
            self.query_collection.fetch_by_items_patient_helped_status_and_rating(
                filter_params
            )
        )
        query: Select = self.query_pagination.apply(query, filter_params)

        if filter_params.exclude_review_fields:
            return self.query_executor.fetch_review_list_with_selected_columns(
                query, filter_params.exclude_review_fields
            )

        return self.query_executor.fetch_review_list(query)

    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.add(review)
        self.session.flush()
        return review

    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.delete(review)
        self.session.flush()
        return review


class _ItemReviewQueryCollection:

    @staticmethod
    def fetch_by_id(review_id: int) -> Select:
        return select(entities.ItemReview).where(entities.ItemReview.id == review_id)

    @staticmethod
    def fetch_all() -> Select:
        return select(entities.ItemReview).distinct()

    @staticmethod
    def fetch_by_items(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_patient(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id)
        )

    @staticmethod
    def fetch_patient_reviews_by_item(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_rating(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_helped_status(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_items_and_patient(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )

    @staticmethod
    def fetch_by_items_and_helped_status(filter_params: schemas.FindItemReviews
                                         ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_items_and_rating(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_patient_and_helped_status(filter_params: schemas.FindItemReviews
                                           ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_patient_and_rating(filter_params: schemas.FindItemReviews) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_helped_status_and_rating(filter_params: schemas.FindItemReviews
                                          ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_items_patient_and_helped_status(filter_params: schemas.FindItemReviews,
                                                 ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped)
        )

    @staticmethod
    def fetch_by_items_patient_and_rating(filter_params: schemas.FindItemReviews
                                          ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_items_helped_status_and_rating(
        filter_params: schemas.FindItemReviews
    ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_patient_helped_status_and_rating(filter_params: schemas.FindItemReviews
                                                  ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )

    @staticmethod
    def fetch_by_items_patient_helped_status_and_rating(
        filter_params: schemas.FindItemReviews,
    ) -> Select:
        return (
            select(entities.ItemReview)
            .distinct()
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids),
                   entities.ItemReview.is_helped == filter_params.is_helped,
                   between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )


class _ItemReviewQueriesPagination:
    def apply(self, query: Select, filter_params: schemas.FindItemReviews) -> Select:
        query = self.set_order(query, filter_params)
        query = self.set_limit(query, filter_params)
        query = self.set_offset(query, filter_params)
        return query

    @staticmethod
    def set_order(query: Select, filter_params: schemas.FindItemReviews) -> Select:
        if filter_params.sort_field is None:
            return query

        sort_field = getattr(entities.ItemReview, filter_params.sort_field)
        return (
            query.order_by(
                desc(sort_field).nullslast()
                if filter_params.sort_direction == 'desc'
                else asc(sort_field).nullslast()
            )
        )

    @staticmethod
    def set_limit(query: Select, filter_params: schemas.FindItemReviews) -> Select:
        if filter_params.limit is None:
            return query

        return query.limit(filter_params.limit)

    @staticmethod
    def set_offset(query: Select, filter_params: schemas.FindItemReviews) -> Select:
        if filter_params.offset is None:
            return query

        return query.offset(filter_params.offset)


class _ItemReviewQueryExecutor:
    def __init__(self, session: Session):
        self.session = session

    def fetch_review(self, query: Select) -> entities.ItemReview | None:
        return self.session.execute(query).scalar_one_or_none()

    def fetch_review_list(self, query: Select) -> Sequence[entities.ItemReview | None]:
        return self.session.execute(query).scalars().all()

    def fetch_review_list_with_selected_columns(self,
                                                query: Select,
                                                exclude_review_fields: list[str]
                                                ) -> Sequence[dtos.ItemReview | None]:
        included_column_names: list[str] = entities.ItemReview.get_field_names(
            exclude_fields=exclude_review_fields
        )
        included_columns: list[InstrumentedAttribute] = [
            getattr(entities.ItemReview, column) for column in included_column_names
        ]
        query: Select = query.with_only_columns(*included_columns,
                                                maintain_column_froms=True)
        result: Sequence[RowMapping | None] = self.session.execute(query).mappings().all()
        return [dtos.ItemReview(**row) for row in result]
