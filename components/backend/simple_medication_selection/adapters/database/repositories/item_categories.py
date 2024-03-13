from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class ItemCategoriesRepo(BaseRepository, interfaces.DiagnosesRepo):

    def fetch_by_id(self, category_id: int) -> entities.ItemCategory | None:
        query = (
            select(entities.ItemCategory)
            .where(entities.ItemCategory.id == category_id)
        )
        return self.session.execute(query).scalars().one_or_none()

    def fetch_by_name(self, name: str) -> entities.ItemCategory | None:
        query = select(entities.ItemCategory).where(entities.ItemCategory.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        self.session.add(item_category)
        self.session.flush()
        return item_category

    def remove(self, item_category: entities.ItemCategory) -> entities.ItemCategory:
        self.session.delete(item_category)
        self.session.flush()
        return item_category
