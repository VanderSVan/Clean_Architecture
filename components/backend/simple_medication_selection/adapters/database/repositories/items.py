from typing import Sequence, Callable

from sqlalchemy import select, desc, func, between, asc, Select
from sqlalchemy.orm import joinedload

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class TreatmentItemsRepo(BaseRepository, interfaces.TreatmentItemsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.items_filter = _TreatmentItemsFilter()

    def fetch_by_id(self,
                    item_id: int,
                    include_reviews: bool
                    ) -> entities.TreatmentItem | None:

        query: Select = (
            select(entities.TreatmentItem)
            .where(entities.TreatmentItem.id == item_id)
        )

        if include_reviews:
            query = query.options(joinedload(entities.TreatmentItem.reviews))
            return self.session.execute(query).scalars().unique().one_or_none()

        return self.session.execute(query).scalars().one_or_none()

    def fetch_all(self,
                  filter_params: schemas.FindTreatmentItemList,
                  include_reviews: bool
                  ) -> Sequence[entities.TreatmentItem | None]:

        query = select(entities.TreatmentItem)
        query = self.items_filter.apply_filters(query, filter_params)

        if include_reviews:
            query = query.options(joinedload(entities.TreatmentItem.reviews))

        return self.session.execute(query).scalars().unique().all()

    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.add(item)
        self.session.flush()
        return item

    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.delete(item)
        self.session.flush()
        return item


class _TreatmentItemsFilter:
    def __init__(self):
        self.filters: list[Callable] = [
            self.only_unique,
            self.by_keywords,
            self.by_category,
            self.by_type,
            self.by_rating,
            self.by_price,
            self.by_helped_status,
            self.by_symptoms,
            self.by_diagnosis,
            self.sort_by_field,
            self.with_offset,
            self.with_limit
        ]

    def apply_filters(self, query: Select, filter_params: schemas.FindTreatmentItemList):
        for filter_method in self.filters:
            query = filter_method(query, filter_params)
        return query

    @staticmethod
    def only_unique(query: Select,
                    filter_params: schemas.FindTreatmentItemList) -> Select:
        return query.distinct()

    @staticmethod
    def by_keywords(query: Select,
                    filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.keywords:
            query = query.where(
                entities.TreatmentItem.title.ilike(f'%{filter_params.keywords}%') |
                entities.TreatmentItem.description.ilike(f'%{filter_params.keywords}%')
            )
        return query

    @staticmethod
    def by_category(query: Select,
                    filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.category_id is not None:
            query = query.where(
                entities.TreatmentItem.category_id == filter_params.category_id
            )

        return query

    @staticmethod
    def by_type(query: Select, filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.type_id is not None:
            query = query.where(entities.TreatmentItem.type_id == filter_params.type_id)

        return query

    @staticmethod
    def by_rating(query: Select, filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.max_rating is not None and filter_params.min_rating is not None:
            return query.where(
                between(entities.TreatmentItem.avg_rating,
                        filter_params.min_rating, filter_params.max_rating)
            )

        elif filter_params.min_rating is not None:
            return query.where(
                entities.TreatmentItem.avg_rating >= filter_params.min_rating
            )

        elif filter_params.max_rating is not None:
            return query.where(
                entities.TreatmentItem.avg_rating <= filter_params.max_rating
            )

        return query

    @staticmethod
    def by_price(query: Select, filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.max_price is not None and filter_params.min_price is not None:
            return query.where(
                between(entities.TreatmentItem.price,
                        filter_params.min_price, filter_params.max_price)
            )

        elif filter_params.min_price is not None:
            return query.where(entities.TreatmentItem.price >= filter_params.min_price)

        elif filter_params.max_price is not None:
            return query.where(entities.TreatmentItem.price <= filter_params.max_price)

        return query

    @staticmethod
    def by_helped_status(query: Select,
                         filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.is_helped is not None:
            query = (
                query
                .join(entities.TreatmentItem.reviews)
                .where(entities.ItemReview.is_helped == filter_params.is_helped)
            )
        return query

    @staticmethod
    def by_symptoms(query: Select,
                    filter_params: schemas.FindTreatmentItemList) -> Select:
        if not filter_params.symptom_ids:
            return query

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if filter_params.match_all_symptoms:
            subquery = (
                subquery
                .having(func.count(entities.Symptom.id.distinct()) ==
                        len(filter_params.symptom_ids))
            )

        subquery = subquery.subquery()

        return query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)

    @staticmethod
    def by_diagnosis(query: Select,
                     filter_params: schemas.FindTreatmentItemList) -> Select:
        if not filter_params.diagnosis_id:
            return query

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.ItemReview.item_id)
            .subquery()
        )
        return query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)

    @staticmethod
    def sort_by_field(query: Select,
                      filter_params: schemas.FindTreatmentItemList) -> Select:
        sort_field = getattr(entities.TreatmentItem, filter_params.sort_field)

        if filter_params.sort_direction == 'desc':
            return query.order_by(desc(sort_field).nullslast())

        return query.order_by(asc(sort_field).nullslast())

    @staticmethod
    def with_limit(query: Select, filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.limit:
            return query.limit(filter_params.limit)
        return query

    @staticmethod
    def with_offset(query: Select,
                    filter_params: schemas.FindTreatmentItemList) -> Select:
        if filter_params.offset:
            return query.offset(filter_params.offset)
        return query
