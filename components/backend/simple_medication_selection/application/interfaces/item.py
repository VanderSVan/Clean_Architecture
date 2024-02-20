from abc import ABC, abstractmethod

from .. import entities


class TreatmentItemsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, item_id: int) -> entities.TreatmentItem | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  limit: int | None,
                  offset: int
                  ) -> list[entities.TreatmentItem] | list[None]:
        ...

    @abstractmethod
    def fetch_by_keywords(self,
                          keywords: str,
                          limit: int | None,
                          offset: int
                          ) -> list[entities.TreatmentItem] | list[None]:
        ...

    def fetch_by_category(self,
                          category_id: int,
                          limit: int | None,
                          offset: int
                          ) -> list[entities.TreatmentItem] | list[None]:
        ...

    def fetch_by_type(self,
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
