from typing import Sequence

from sqlalchemy import select, asc, desc

from simple_medication_selection.application import interfaces, entities, schemas
from .base import BaseRepository


class ItemTypesRepo(BaseRepository, interfaces.ItemTypesRepo):

    def fetch_by_id(self, item_type_id: int) -> entities.ItemType | None:
        query = select(entities.ItemType).where(entities.ItemType.id == item_type_id)
        return self.session.execute(query).scalars().one_or_none()
    
    def fetch_by_name(self, name: str) -> entities.ItemType | None:
        query = select(entities.ItemType).where(entities.ItemType.name == name)
        return self.session.execute(query).scalars().one_or_none()
    
    def fetch_all(self,
                  filter_params: schemas.FindItemTypes
                  ) -> Sequence[entities.ItemType | None]:
        query = (
            select(entities.ItemType)
            .limit(filter_params.limit)
            .offset(filter_params.offset)
            .order_by(
                desc(getattr(entities.ItemType, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.ItemType, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def search_by_name(self,
                       filter_params: schemas.FindItemTypes
                       ) -> Sequence[entities.ItemType | None]:
        query = (
            select(entities.ItemType)
            .where(entities.ItemType.name.ilike(f'%{filter_params.keywords}%'))
            .offset(filter_params.offset)
            .limit(filter_params.limit)
            .order_by(
                desc(getattr(entities.ItemType, filter_params.sort_field))
                if filter_params.sort_direction == 'desc'
                else asc(getattr(entities.ItemType, filter_params.sort_field))
            )
        )

        return self.session.execute(query).scalars().all()

    def add(self, item_type: entities.ItemType) -> entities.ItemType:
        self.session.add(item_type)
        self.session.flush()
        return item_type

    def remove(self, item_type: entities.ItemType) -> entities.ItemType:
        self.session.delete(item_type)
        self.session.flush()
        return item_type
