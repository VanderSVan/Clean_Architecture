from typing import Sequence

from sqlalchemy import select, asc, desc

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class ItemCategoriesRepo(BaseRepository, interfaces.ItemCategoriesRepo):

    def fetch_by_id(self, category_id: int) -> entities.ItemCategory | None:
        query = (
            select(entities.ItemCategory)
            .where(entities.ItemCategory.id == category_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.ItemCategory | None:
        query = select(entities.ItemCategory).where(entities.ItemCategory.name == name)
        return self.session.execute(query).scalars().one_or_none()
    
    def fetch_all(self,
                  filter_params: schemas.FindItemCategories
                  ) -> Sequence[entities.ItemCategory | None]:
        query = (
            select(entities.ItemCategory)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .order_by(
                desc(getattr(entities.ItemCategory, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.ItemCategory, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def search_by_name(self,
                       filter_params: schemas.FindItemCategories
                       ) -> Sequence[entities.ItemCategory | None]:
        query = (
            select(entities.ItemCategory)
            .where(entities.ItemCategory.name.ilike(f'%{filter_params.keywords}%'))
            .offset(filter_params.offset)
            .limit(filter_params.limit)
            .order_by(
                desc(getattr(entities.ItemCategory, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.ItemCategory, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def add(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        self.session.add(item_category)
        self.session.flush()
        return item_category

    def remove(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        self.session.delete(item_category)
        self.session.flush()
        return item_category
