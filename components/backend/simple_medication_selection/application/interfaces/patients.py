from abc import ABC, abstractmethod
from typing import Sequence

from simple_medication_selection.application import entities, schemas


class PatientsRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, patient_id: int) -> entities.Patient | None:
        ...

    @abstractmethod
    def fetch_by_nickname(self, nickname: str) -> entities.Patient | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindPatients
                  ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_gender(self,
                        filter_params: schemas.FindPatients
                        ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_age(self,
                     filter_params: schemas.FindPatients
                     ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_skin_type(self,
                           filter_params: schemas.FindPatients
                           ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_gender_and_age(self,
                                filter_params: schemas.FindPatients
                                ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_gender_and_skin_type(self,
                                      filter_params: schemas.FindPatients
                                      ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_age_and_skin_type(self,
                                   filter_params: schemas.FindPatients
                                   ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def fetch_by_gender_age_and_skin_type(self,
                                          filter_params: schemas.FindPatients
                                          ) -> Sequence[entities.Patient]:
        ...

    @abstractmethod
    def add(self, patient: entities.Patient) -> entities.Patient:
        ...

    @abstractmethod
    def remove(self, patient: entities.Patient) -> entities.Patient:
        ...
