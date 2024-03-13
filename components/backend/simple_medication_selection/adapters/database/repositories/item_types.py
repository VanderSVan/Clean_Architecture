from sqlalchemy import select

from simple_medication_selection.application import interfaces, entities
from .base import BaseRepository


class ItemTypesRepo(BaseRepository, interfaces.ItemTypesRepo):

    def fetch_by_id(self, item_type_id: int) -> entities.ItemType | None:
        query = select(entities.ItemType).where(entities.ItemType.id == item_type_id)
        return self.session.execute(query).scalars().one_or_none()
    
    def fetch_by_name(self, name: str) -> entities.ItemType | None:
        query = select(entities.ItemType).where(entities.ItemType.name == name)
        return self.session.execute(query).scalars().one_or_none()

    def add(self, item_type: entities.ItemType) -> entities.ItemType:
        self.session.add(item_type)
        self.session.flush()
        return item_type

    def remove(self, item_type: entities.ItemType) -> entities.ItemType:
        self.session.delete(item_type)
        self.session.flush()
        return item_type
