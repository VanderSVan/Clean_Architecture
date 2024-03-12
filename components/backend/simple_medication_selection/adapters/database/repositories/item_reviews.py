from typing import Sequence, Literal

from sqlalchemy import select, desc, asc

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class ItemReviewsRepo(BaseRepository, interfaces.ItemReviewsRepo):
    def fetch_by_id(self, review_id: int) -> entities.ItemReview | None:
        query = (
            select(entities.ItemReview)
            .where(entities.ItemReview.id == review_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  order_field: str,
                  order_direction: Literal['asc', 'desc'],
                  limit: int,
                  offset: int
                  ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_all_by_item(self,
                          item_id: int,
                          order_field: str,
                          order_direction: Literal['asc', 'desc'],
                          limit: int,
                          offset: int
                          ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(entities.ItemReview.item_id == item_id)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_reviews_by_patient(self,
                                 patient_id: int,
                                 order_field: str,
                                 order_direction: Literal['asc', 'desc'],
                                 limit: int,
                                 offset: int
                                 ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(entities.ItemReview.patient_id == patient_id)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_patient_reviews_by_item(self,
                                      patient_id: int,
                                      item_id: int,
                                      order_field: str,
                                      order_direction: Literal['asc', 'desc'],
                                      limit: int,
                                      offset: int
                                      ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(
                entities.ItemReview.patient_id == patient_id,
                   entities.ItemReview.item_id == item_id
            )
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_rating(self,
                        min_rating: float,
                        max_rating: float | None,
                        order_field: str,
                        order_direction: Literal['asc', 'desc'],
                        limit: int,
                        offset: int
                        ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(entities.ItemReview.rating.between(min_rating, max_rating))
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_helped_status(self,
                               is_helped: bool,
                               order_field: str,
                               order_direction: Literal['asc', 'desc'],
                               limit: int,
                               offset: int
                               ) -> Sequence[entities.ItemReview | None]:
        query = (
            select(entities.ItemReview)
            .where(entities.ItemReview.is_helped == is_helped)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.ItemReview, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.ItemReview, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def add(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.add(review)
        self.session.flush()
        return review

    def remove(self, review: entities.ItemReview) -> entities.ItemReview:
        self.session.delete(review)
        self.session.flush()
        return review
