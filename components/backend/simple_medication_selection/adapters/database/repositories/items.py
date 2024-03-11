from typing import Sequence, Literal

from sqlalchemy import select, desc, func, between, distinct, asc

from simple_medication_selection.application import interfaces, entities, dtos
from .base import BaseRepository


class TreatmentItemsRepo(BaseRepository, interfaces.TreatmentItemsRepo):

    def fetch_by_id(self, item_id: int) -> entities.TreatmentItem | None:
        query = (
            select(entities.TreatmentItem)
            .where(entities.TreatmentItem.id == item_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  order_field: str,
                  order_direction: Literal['asc', 'desc'],
                  limit: int | None,
                  offset: int | None
                  ) -> list[dtos.ItemGetSchema | None]:
        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemGetSchema(**row) for row in result]

    def fetch_all_with_reviews(self,
                               order_field: str,
                               order_direction: Literal['asc', 'desc'],
                               limit: int | None,
                               offset: int | None
                               ) -> Sequence[entities.TreatmentItem | None]:
        query = (
            select(entities.TreatmentItem)
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )
        return self.session.execute(query).scalars().all()

    def fetch_by_keywords(self,
                          keywords: str,
                          order_field: str,
                          order_direction: Literal['asc', 'desc'],
                          limit: int | None,
                          offset: int | None
                          ) -> list[dtos.ItemGetSchema | None]:
        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
            .where(
                entities.TreatmentItem.title.ilike(f'%{keywords}%')
                | entities.TreatmentItem.description.ilike(f'%{keywords}%')
            )
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemGetSchema(**row) for row in result]

    def fetch_by_keywords_with_reviews(self,
                                       keywords: str,
                                       order_field: str,
                                       order_direction: Literal['asc', 'desc'],
                                       limit: int | None,
                                       offset: int | None
                                       ) -> Sequence[entities.TreatmentItem | None]:
        query = (
            select(entities.TreatmentItem)
            .where(
                entities.TreatmentItem.title.ilike(f'%{keywords}%')
                | entities.TreatmentItem.description.ilike(f'%{keywords}%')
            )
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        return self.session.execute(query).scalars().all()

    def fetch_by_category(self,
                          category_id: int,
                          order_field: str,
                          order_direction: Literal['asc', 'desc'],
                          limit: int | None,
                          offset: int | None
                          ) -> list[dtos.ItemGetSchema | None]:
        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
            .where(entities.TreatmentItem.category_id == category_id)
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemGetSchema(**row) for row in result]

    def fetch_by_type(self,
                      type_id: int,
                      order_field: str,
                      order_direction: Literal['asc', 'desc'],
                      limit: int | None,
                      offset: int | None
                      ) -> list[dtos.ItemGetSchema | None]:
        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
            .where(entities.TreatmentItem.type_id == type_id)
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemGetSchema(**row) for row in result]

    def fetch_by_rating(self,
                        min_rating: float,
                        max_rating: float,
                        order_field: str,
                        order_direction: Literal['asc', 'desc'],
                        limit: int | None,
                        offset: int | None
                        ) -> list[dtos.ItemGetSchema | None]:
        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating,
            )
            .where(between(entities.TreatmentItem.avg_rating, min_rating, max_rating))
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemGetSchema(**row) for row in result]

    def fetch_by_helped_status(
        self,
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusGetSchema | None]:

        subquery = (
            select(
                entities.ItemReview.item_id,
                entities.ItemReview.is_helped,
            )
            .group_by(entities.ItemReview.item_id, entities.ItemReview.is_helped)
            .subquery()
        )

        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating,
                subquery.c.is_helped,
            )
            .join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
            .where(subquery.c.is_helped == is_helped)
            .offset(offset)
            .limit(limit)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemWithHelpedStatusGetSchema(**row) for row in result]

    def fetch_by_symptoms_and_helped_status(
        self,
        symptom_ids: list[int],
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusSymptomsGetSchema | None]:

        subquery = (
            select(
                entities.ItemReview.item_id,
                entities.ItemReview.is_helped,
                func.array_agg(
                    distinct(entities.Symptom.id)).label("overlapping_symptom_ids")
            )
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(
                entities.ItemReview.is_helped == is_helped,
                entities.Symptom.id.in_(symptom_ids)
            )
            .group_by(entities.ItemReview.item_id, entities.ItemReview.is_helped)
            .subquery()
        )

        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating,
                subquery.c.is_helped,
                subquery.c.overlapping_symptom_ids,
            )
            .join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemWithHelpedStatusSymptomsGetSchema(**row) for row in result]

    def fetch_by_diagnosis_and_helped_status(
        self,
        diagnosis_id: int,
        is_helped: bool,
        order_field: str,
        order_direction: Literal['asc', 'desc'],
        limit: int | None,
        offset: int | None
    ) -> list[dtos.ItemWithHelpedStatusDiagnosisGetSchema | None]:

        subquery = (
            select(
                entities.ItemReview.item_id,
                entities.ItemReview.is_helped,
                entities.Diagnosis.id.label("diagnosis_id"),
            )
            .join(entities.MedicalBook.item_reviews)
            .join(entities.Diagnosis)
            .where(
                entities.ItemReview.is_helped == is_helped,
                entities.Diagnosis.id == diagnosis_id
            )
            .group_by(entities.ItemReview.item_id,
                      entities.ItemReview.is_helped,
                      entities.Diagnosis.id)
            .subquery()
        )

        query = (
            select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating,
                subquery.c.is_helped,
                subquery.c.diagnosis_id,
            )
            .join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
            .limit(limit)
            .offset(offset)
            .order_by(
                desc(getattr(entities.TreatmentItem, order_field)).nullslast()
                if order_direction == 'desc'
                else asc(getattr(entities.TreatmentItem, order_field)).nullslast()
            )
        )

        result = self.session.execute(query).mappings()
        return [dtos.ItemWithHelpedStatusDiagnosisGetSchema(**row) for row in result]

    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.add(item)
        self.session.flush()
        return item

    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.delete(item)
        self.session.flush()
        return item
