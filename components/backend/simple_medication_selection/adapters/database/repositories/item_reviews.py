from typing import Sequence

from sqlalchemy import select, desc, asc, between, Select

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class ItemReviewsRepo(BaseRepository, interfaces.ItemReviewsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.query_pagination = _ItemReviewQueriesPagination()

    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        query: Select = (
            select(entities.ItemReview)
            .where(entities.ItemReview.id == review_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindItemReviews,
                  ) -> Sequence[entities.ItemReview | None]:
        query: Select = select(entities.ItemReview)
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_item(self,
                      filter_params: schemas.FindItemReviews,
                      ) -> Sequence[entities.ItemReview | None]:
        query: Select = (
            select(entities.ItemReview)
            .where(entities.ItemReview.item_id.in_(filter_params.item_ids))
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_patient(self,
                         filter_params: schemas.FindItemReviews,
                         ) -> Sequence[entities.ItemReview | None]:
        query: Select = (
            select(entities.ItemReview)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_patient_reviews_by_item(self,
                                      filter_params: schemas.FindItemReviews,
                                      ) -> Sequence[entities.ItemReview | None]:
        query: Select = (
            select(entities.ItemReview)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == filter_params.patient_id,
                   entities.ItemReview.item_id.in_(filter_params.item_ids))
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_rating(self,
                        filter_params: schemas.FindItemReviews,
                        ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(between(entities.ItemReview.item_rating,
                           filter_params.min_rating, filter_params.max_rating))
        )
        query = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def fetch_by_helped_status(self,
                               filter_params: schemas.FindItemReviews,
                               ) -> Sequence[entities.ItemReview | None]:
        query: Select = (
            select(entities.ItemReview)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
        )
        query: Select = self.query_pagination.apply(query, filter_params)
        return self.session.execute(query).scalars().all()

    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.add(review)
        self.session.flush()
        return review

    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.delete(review)
        self.session.flush()
        return review


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
