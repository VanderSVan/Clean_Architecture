from dataclasses import asdict
from typing import Sequence

from falcon import status_codes

from spectree import Response
from ..spec import spectree

from simple_medication_selection.application import services, entities, dtos, schemas


class MedicalBooks:

    def __init__(self, medical_book: services.MedicalBook):
        self.med_book = medical_book

    @spectree.validate(
        query=schemas.FindMedicalBooks,
        resp=Response(HTTP_200=list[dtos.MedicalBook]),
        tags=["Medical books"]
    )
    def on_get(self, req, resp):
        """
        Поиск медицинских карт.
        """
        filter_params = schemas.FindMedicalBooks(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBook | None] = (
            self.med_book.find_med_books(filter_params)
        )

        resp.media = [med_book.dict() for med_book in found_books if med_book is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindMedicalBooks,
        resp=Response(HTTP_200=list[dtos.MedicalBookWithSymptoms]),
        tags=["Medical books with symptoms"]
    )
    def on_get_with_symptoms(self, req, resp):
        """
        Поиск медицинских карт с симптомами.
        """
        filter_params = schemas.FindMedicalBooks(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBookWithSymptoms | None] = (
            self.med_book.find_med_books_with_symptoms(filter_params)
        )

        resp.media = [med_book.dict() for med_book in found_books if med_book is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindMedicalBooks,
        resp=Response(HTTP_200=list[dtos.MedicalBookWithItemReviews]),
        tags=["Medical books with reviews"]
    )
    def on_get_with_reviews(self, req, resp):
        """
        Поиск медицинских карт с отзывами.
        """
        filter_params = schemas.FindMedicalBooks(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBookWithItemReviews | None] = (
            self.med_book.find_med_books_with_reviews(filter_params)
        )

        resp.media = [med_book.dict() for med_book in found_books if med_book is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindMedicalBooks,
        resp=Response(HTTP_200=list[dtos.MedicalBookWithSymptomsAndItemReviews]),
        tags=["Medical books with symptoms and reviews"]
    )
    def on_get_with_symptoms_and_reviews(self, req, resp):
        """
        Поиск медицинских карт с симптомами и отзывами.
        """
        filter_params = schemas.FindMedicalBooks(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: Sequence[entities.MedicalBook | None] = (
            self.med_book.find_med_books_with_symptoms_and_reviews(filter_params)
        )

        resp.media = [asdict(med_book) for med_book in found_books if med_book is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBook),
        tags=["Medical books"]
    )
    def on_get_by_id(self, req, resp, medical_book_id):
        """
        Получение медицинской карты по идентификатору.
        """
        med_book: dtos.MedicalBook = self.med_book.get_med_book(medical_book_id)

        resp.media = med_book.dict()
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptoms),
        tags=["Medical books with symptoms"]
    )
    def on_get_by_id_with_symptoms(self, req, resp, medical_book_id):
        """
        Получение медицинской карты с симптомами по идентификатору.
        """
        med_book: dtos.MedicalBookWithSymptoms = (
            self.med_book.get_med_book_with_symptoms(medical_book_id)
        )

        resp.media = med_book.dict()
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithItemReviews),
        tags=["Medical books with reviews"]
    )
    def on_get_by_id_with_reviews(self, req, resp, medical_book_id):
        """
        Получение медицинской карты с отзывами по идентификатору.
        """
        med_book: dtos.MedicalBookWithItemReviews = (
            self.med_book.get_med_book_with_reviews(medical_book_id)
        )

        resp.media = med_book.dict()
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books with symptoms and reviews"]
    )
    def on_get_by_id_with_symptoms_and_reviews(self, req, resp, medical_book_id):
        """
        Получение медицинской карты с симптомами и отзывами по идентификатору.
        """
        med_book: entities.MedicalBook = (
            self.med_book.get_med_book_with_symptoms_and_reviews(medical_book_id)
        )

        resp.media = asdict(med_book)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewMedicalBookInfo,
        resp=Response(HTTP_201=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_post_new(self, req, resp):
        """
        Создание медицинской карты.
        """
        new_med_book_info = dtos.NewMedicalBookInfo(**req.media)
        new_med_book: entities.MedicalBook = self.med_book.add(new_med_book_info)

        resp.media = asdict(new_med_book)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        json=dtos.UpdatedMedicalBookInfo,
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_put_by_id(self, req, resp, medical_book_id: int):
        """
        Изменение медицинской карты.
        """
        req.media.update({'id': medical_book_id})
        updated_med_book_info = dtos.UpdatedMedicalBookInfo(**req.media)
        updated_med_book: entities.MedicalBook = (
            self.med_book.change(updated_med_book_info)
        )

        resp.media = asdict(updated_med_book)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"medical_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_delete_by_id(self, req, resp, medical_book_id):
        """
        Удаление медицинской карты.
        """
        removed_med_book: entities.MedicalBook = self.med_book.delete(medical_book_id)

        resp.media = asdict(removed_med_book)
        resp.status = status_codes.HTTP_200
