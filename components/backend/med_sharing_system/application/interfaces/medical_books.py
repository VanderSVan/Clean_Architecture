from abc import ABC, abstractmethod
from typing import Sequence

from .. import entities, schemas


class MedicalBooksRepo(ABC):

    @abstractmethod
    def fetch_by_id(self,
                    med_book_id: int,
                    *,
                    include_symptoms: bool,
                    include_reviews: bool
                    ) -> entities.MedicalBook | None:
        ...

    @abstractmethod
    def fetch_all(self,
                  filter_params: schemas.FindMedicalBooks,
                  *,
                  include_symptoms: bool,
                  include_reviews: bool
                  ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_symptoms(self,
                          filter_params: schemas.FindMedicalBooks,
                          *,
                          include_symptoms: bool,
                          include_reviews: bool
                          ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_matching_all_symptoms(self,
                                       filter_params: schemas.FindMedicalBooks,
                                       *,
                                       include_symptoms: bool,
                                       include_reviews: bool
                                       ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis(self,
                           filter_params: schemas.FindMedicalBooks,
                           *,
                           include_symptoms: bool,
                           include_reviews: bool
                           ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_and_symptoms(self,
                                        filter_params: schemas.FindMedicalBooks,
                                        *,
                                        include_symptoms: bool,
                                        include_reviews: bool
                                        ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status(self,
                               filter_params: schemas.FindMedicalBooks,
                               *,
                               include_symptoms: bool,
                               include_reviews: bool
                               ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_and_symptoms(self,
                                            filter_params: schemas.FindMedicalBooks,
                                            *,
                                            include_symptoms: bool,
                                            include_reviews: bool
                                            ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_and_diagnosis(self,
                                             filter_params: schemas.FindMedicalBooks,
                                             *,
                                             include_symptoms: bool,
                                             include_reviews: bool
                                             ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient(self,
                         filter_params: schemas.FindMedicalBooks,
                         *,
                         include_symptoms: bool,
                         include_reviews: bool
                         ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_symptoms(self,
                                      filter_params: schemas.FindMedicalBooks,
                                      *,
                                      include_symptoms: bool,
                                      include_reviews: bool
                                      ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_helped_status(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_and_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_diagnosis(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_items(self,
                       filter_params: schemas.FindMedicalBooks,
                       *,
                       include_symptoms: bool,
                       include_reviews: bool
                       ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_and_items(self,
                                   filter_params: schemas.FindMedicalBooks,
                                   *,
                                   include_symptoms: bool,
                                   include_reviews: bool
                                   ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_helped_status(self,
                                         filter_params: schemas.FindMedicalBooks,
                                         *,
                                         include_symptoms: bool,
                                         include_reviews: bool
                                         ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_diagnosis(self,
                                     filter_params: schemas.FindMedicalBooks,
                                     *,
                                     include_symptoms: bool,
                                     include_reviews: bool
                                     ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_items_and_symptoms(self,
                                    filter_params: schemas.FindMedicalBooks,
                                    *,
                                    include_symptoms: bool,
                                    include_reviews: bool
                                    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_helped_status_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_and_items(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def fetch_by_patient_helped_status_diagnosis_items_with_matching_all_symptoms(
        self,
        filter_params: schemas.FindMedicalBooks,
        *,
        include_symptoms: bool,
        include_reviews: bool
    ) -> Sequence[entities.MedicalBook | None]:
        ...

    @abstractmethod
    def add(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...

    @abstractmethod
    def remove(self, med_book: entities.MedicalBook) -> entities.MedicalBook:
        ...
