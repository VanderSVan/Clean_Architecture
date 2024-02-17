from abc import ABC, abstractmethod

from .. import entities


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def get_by_id(self, code: str) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def find_by_keywords(self,
                         search: str,
                         limit: int,
                         offset: int
                         ) -> list[entities.TreatmentItem] | list[None]:
        ...

    def find_by_category_id(self,
                            category_id: int,
                            limit: int | None,
                            offset: int
                            ) -> list[entities.TreatmentItem] | list[None]:
        ...

    def find_by_type_id(self,
                        type_id: int,
                        limit: int | None,
                        offset: int
                        ) -> list[entities.TreatmentItem] | list[None]:
        ...

    @abstractmethod
    def add(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...

    @abstractmethod
    def remove(self, item: entities.TreatmentItem) -> entities.TreatmentItem:
        ...
