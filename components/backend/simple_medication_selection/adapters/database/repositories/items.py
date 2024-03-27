from typing import Sequence, Callable

from sqlalchemy import select, desc, func, between, asc, Select

from simple_medication_selection.application import interfaces, entities, dtos, schemas
from .base import BaseRepository


class _TreatmentItemsFilter:
    def __init__(self):
        self.filters: list[Callable] = [
            self.by_keywords,
            self.by_category,
            self.by_type,
            self.by_rating,
            self.by_price,
            self.sort_by_field,
            self.apply_pagination,
        ]

    def apply_filters(self, query: Select, filter_params: schemas.FindTreatmentItems):
        for filter_method in self.filters:
            query = filter_method(query, filter_params)
        return query

    @staticmethod
    def by_keywords(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
        if filter_params.keywords:
            query = query.where(
                entities.TreatmentItem.title.ilike(f'%{filter_params.keywords}%') |
                entities.TreatmentItem.description.ilike(f'%{filter_params.keywords}%')
            )
        return query

    @staticmethod
    def by_category(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
        if filter_params.category_id is not None:
            query = query.where(
                entities.TreatmentItem.category_id == filter_params.category_id
            )

        return query

    @staticmethod
    def by_type(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
        if filter_params.type_id is not None:
            query = query.where(entities.TreatmentItem.type_id == filter_params.type_id)

        return query

    @staticmethod
    def by_rating(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
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
    def by_price(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
        if filter_params.max_price is not None and filter_params.min_price is not None:
            return query.where(
                between(entities.TreatmentItem.price, filter_params.min_price,
                        filter_params.max_price)
            )

        elif filter_params.min_price is not None:
            return query.where(entities.TreatmentItem.price >= filter_params.min_price)

        elif filter_params.max_price is not None:
            return query.where(entities.TreatmentItem.price <= filter_params.max_price)

        return query

    @staticmethod
    def sort_by_field(query: Select, filter_params: schemas.FindTreatmentItems) -> Select:
        sort_field = getattr(entities.TreatmentItem, filter_params.sort_field)

        if filter_params.sort_direction == 'desc':
            return query.order_by(desc(sort_field).nullslast())

        return query.order_by(asc(sort_field).nullslast())

    @staticmethod
    def apply_pagination(query: Select, filter_params):
        return query.offset(filter_params.offset).limit(filter_params.limit)


class TreatmentItemsRepo(BaseRepository, interfaces.TreatmentItemsRepo):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._filter = _TreatmentItemsFilter()

    def fetch_by_id(self,
                    item_id: int,
                    with_reviews: bool
                    ) -> dtos.TreatmentItem | None:

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
        query = query.where(entities.TreatmentItem.id == item_id)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().one_or_none()

        row = result.mappings().first()
        return dtos.TreatmentItem(**row) if row else None

    def fetch_all(self,
                  filter_params: schemas.FindTreatmentItems,
                  with_reviews: bool
                  ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(
                entities.TreatmentItem.id,
                entities.TreatmentItem.title,
                entities.TreatmentItem.price,
                entities.TreatmentItem.description,
                entities.TreatmentItem.category_id,
                entities.TreatmentItem.type_id,
                entities.TreatmentItem.avg_rating
            )
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .where(entities.ItemReview.is_helped == filter_params.is_helped)
            .group_by(entities.ItemReview.item_id)
            .subquery()
        )

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating,
                           )
        query = query.join(subquery, subquery.c.item_id == entities.TreatmentItem.id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if filter_params.match_all_symptoms:
            subquery = (subquery
                        .having(func.count(entities.Symptom.id.distinct()) ==
                                len(filter_params.symptom_ids))
                        )
        subquery = subquery.subquery()

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_diagnosis(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.ItemReview.item_id)
            .subquery()
        )
        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_symptoms_and_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.ItemReview.item_id, entities.ItemReview.is_helped)
        )
        if filter_params.match_all_symptoms:
            subquery = (subquery
                        .having(func.count(entities.Symptom.id.distinct()) ==
                                len(filter_params.symptom_ids))
                        )
        subquery = subquery.subquery()

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_diagnosis_and_helped_status(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id)
            .group_by(entities.ItemReview.item_id)
            .subquery()
        )

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.ItemWithDiagnosis(**row) for row in result.mappings()]

    def fetch_by_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if filter_params.match_all_symptoms:
            subquery = (subquery
                        .having(func.count(entities.Symptom.id.distinct()) ==
                                len(filter_params.symptom_ids))
                        )
        subquery = subquery.subquery()

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def fetch_by_helped_status_diagnosis_symptoms(
        self,
        filter_params: schemas.FindTreatmentItems,
        with_reviews: bool
    ) -> Sequence[dtos.TreatmentItem | entities.TreatmentItem | None]:

        subquery = (
            select(entities.ItemReview.item_id)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .where(entities.ItemReview.is_helped == filter_params.is_helped,
                   entities.MedicalBook.diagnosis_id == filter_params.diagnosis_id,
                   entities.Symptom.id.in_(filter_params.symptom_ids))
            .group_by(entities.ItemReview.item_id)
        )
        if filter_params.match_all_symptoms:
            subquery = (subquery
                        .having(func.count(entities.Symptom.id.distinct()) ==
                                len(filter_params.symptom_ids))
                        )
        subquery = subquery.subquery()

        if with_reviews:
            query = select(entities.TreatmentItem)
        else:
            query = select(entities.TreatmentItem.id,
                           entities.TreatmentItem.title,
                           entities.TreatmentItem.price,
                           entities.TreatmentItem.description,
                           entities.TreatmentItem.category_id,
                           entities.TreatmentItem.type_id,
                           entities.TreatmentItem.avg_rating)

        query = query.join(subquery, entities.TreatmentItem.id == subquery.c.item_id)
        query = self._filter.apply_filters(query, filter_params)

        result = self.session.execute(query)
        if with_reviews:
            return result.scalars().all()
        return [dtos.TreatmentItem(**row) for row in result.mappings()]

    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.add(item)
        self.session.flush()
        return item

    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        self.session.delete(item)
        self.session.flush()
        return item
