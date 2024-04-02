from abc import ABC, abstractmethod
from typing import Sequence

from .. import entities, dtos, schemas


class MedicalBooksRepo(ABC):

    @abstractmethod
    def fetch_by_id(self, med_book_id: int) -> dtos.MedicalBook | None:
        ...

    @abstractmethod
    def fetch_by_id_with_symptoms(self,
                                  med_book_id: int
                                  ) -> dtos.MedicalBookWithSymptoms | None:
        ...

    @abstractmethod
    def fetch_by_id_with_reviews(self,
                                 med_book_id: int
                                 ) -> dtos.MedicalBookWithItemReviews | None:
        ...

    @abstractmethod
    def fetch_by_id_with_symptoms_and_reviews(self,
                                              med_book_id: int
                                              ) -> entities.MedicalBook | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindMedicalBooks
                  ) -> list[dtos.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms(self,
                          filter_params: schemas.FindMedicalBooks
                          ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_matching_all_symptoms(self,
                                       filter_params: schemas.FindMedicalBooks
                                       ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis(self,
                           filter_params: schemas.FindMedicalBooks
                           ) -> list[dtos.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_and_symptoms(self,
                                        filter_params: schemas.FindMedicalBooks
                                        ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(self,
                               filter_params: schemas.FindMedicalBooks
                               ) -> list[dtos.MedicalBookWithItemReviews | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_and_symptoms(self,
                                            filter_params: schemas.FindMedicalBooks
                                            ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[dtos.MedicalBookWithItemReviews | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient(self,
                         filter_params: schemas.FindPatientMedicalBooks
                         ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_symptoms(self,
                                      filter_params: schemas.FindPatientMedicalBooks,
                                      ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_patient_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_helped_status(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithItemReviews | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithItemReviews | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBookWithSymptoms | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_diagnosis(
        self,
        filter_params: schemas.FindPatientMedicalBooks
    ) -> list[dtos.MedicalBook | None]:
        ...

    @abstractmethod
    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...
