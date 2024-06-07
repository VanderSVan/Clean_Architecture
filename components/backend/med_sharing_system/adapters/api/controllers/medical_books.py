from falcon import status_codes
from spectree import Response

from med_sharing_system.adapters.api import schemas as api_schemas
from med_sharing_system.adapters.api.spec import spectree
from med_sharing_system.application import services, dtos


class MedicalBooks:

    def __init__(self, medical_book: services.MedicalBook):
        self.med_book = medical_book

    @spectree.validate(
        query=api_schemas.SearchMedicalBooks,
        resp=Response(HTTP_200=list[api_schemas.MedicalBookOutput]),
        tags=["Medical books"]
    )
    def on_get(self, req, resp):
        """
        Поиск медицинских карт.
        """
        filter_params = api_schemas.SearchMedicalBooks(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            exclude_med_book_fields=req.context.query.exclude_med_book_fields,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBook | None] = (
            self.med_book.find_med_books(filter_params)
        )

        resp.media = [med_book.dict(exclude_unset=True, exclude_none=True,
                                    exclude={*filter_params.exclude_med_book_fields})
                      for med_book in found_books if med_book is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=api_schemas.SearchMedicalBooksWithSymptoms,
        resp=Response(HTTP_200=list[api_schemas.MedicalBookWithSymptomsOutput]),
        tags=["Medical books with symptoms"]
    )
    def on_get_with_symptoms(self, req, resp):
        """
        Поиск медицинских карт с симптомами.
        """
        filter_params = api_schemas.SearchMedicalBooksWithSymptoms(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            exclude_med_book_fields=req.context.query.exclude_med_book_fields,
            exclude_symptom_fields=req.context.query.exclude_symptom_fields,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBookWithSymptoms | None] = (
            self.med_book.find_med_books_with_symptoms(filter_params)
        )

        resp.media = []
        for med_book in found_books:
            if med_book is not None:
                med_book_with_symptoms: dict = med_book.dict(
                    exclude_unset=True, exclude_none=True,
                    exclude={*filter_params.exclude_med_book_fields}
                )
                symptoms: list[dict] = [
                    symptom.dict(exclude_unset=True, exclude_none=True,
                                 exclude={*filter_params.exclude_symptom_fields})
                    for symptom in med_book.symptoms
                ]
                med_book_with_symptoms.update({'symptoms': symptoms})
                resp.media.append(med_book_with_symptoms)

        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=api_schemas.SearchMedicalBooksWithItemReviews,
        resp=Response(HTTP_200=list[api_schemas.MedicalBookWithItemReviewsOutput]),
        tags=["Medical books with reviews"]
    )
    def on_get_with_reviews(self, req, resp):
        """
        Поиск медицинских карт с отзывами.
        """
        filter_params = api_schemas.SearchMedicalBooksWithItemReviews(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            exclude_med_book_fields=req.context.query.exclude_med_book_fields,
            exclude_item_review_fields=req.context.query.exclude_item_review_fields,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBookWithItemReviews | None] = (
            self.med_book.find_med_books_with_reviews(filter_params)
        )

        resp.media = []
        for med_book in found_books:
            if med_book is not None:
                med_book_with_reviews: dict = med_book.dict(
                    exclude_unset=True, exclude_none=True,
                    exclude={*filter_params.exclude_med_book_fields}
                )
                item_reviews: list[dict] = [
                    item_review.dict(exclude_unset=True,
                                     exclude_none=True,
                                     exclude={*filter_params.exclude_item_review_fields})
                    for item_review in med_book.item_reviews
                ]
                med_book_with_reviews.update({'item_reviews': item_reviews})
                resp.media.append(med_book_with_reviews)

        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=api_schemas.SearchMedicalBooksWithSymptomsAndItemReviews,
        resp=Response(
            HTTP_200=list[api_schemas.MedicalBookWithSymptomsAndItemReviewsOutput]
        ),
        tags=["Medical books with symptoms and reviews"]
    )
    def on_get_with_symptoms_and_reviews(self, req, resp):
        """
        Поиск медицинских карт с симптомами и отзывами.
        """
        filter_params = api_schemas.SearchMedicalBooksWithSymptomsAndItemReviews(
            patient_id=req.context.query.patient_id,
            item_ids=req.context.query.item_ids,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            exclude_med_book_fields=req.context.query.exclude_med_book_fields,
            exclude_symptom_fields=req.context.query.exclude_symptom_fields,
            exclude_item_review_fields=req.context.query.exclude_item_review_fields,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_books: list[dtos.MedicalBookWithSymptomsAndItemReviews | None] = (
            self.med_book.find_med_books_with_symptoms_and_reviews(filter_params)
        )

        resp.media = []
        for med_book in found_books:
            if med_book is not None:
                med_book_with_symptoms_and_reviews: dict = med_book.dict(
                    exclude_unset=True, exclude_none=True,
                    exclude={*filter_params.exclude_med_book_fields}
                )
                symptoms: list[dict] = [
                    symptom.dict(exclude_unset=True, exclude_none=True,
                                 exclude={*filter_params.exclude_symptom_fields})
                    for symptom in med_book.symptoms
                ]
                item_reviews: list[dict] = [
                    item_review.dict(exclude_unset=True, exclude_none=True,
                                     exclude={*filter_params.exclude_item_review_fields})
                    for item_review in med_book.item_reviews
                ]
                med_book_with_symptoms_and_reviews.update({
                    'symptoms': symptoms,
                    'item_reviews': item_reviews
                })
                resp.media.append(med_book_with_symptoms_and_reviews)

        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBook),
        tags=["Medical books"]
    )
    def on_get_by_id(self, req, resp, med_book_id):
        """
        Получение медицинской карты по идентификатору.
        """
        med_book: dtos.MedicalBook = self.med_book.get_med_book(med_book_id)

        resp.media = med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptoms),
        tags=["Medical books with symptoms"]
    )
    def on_get_by_id_with_symptoms(self, req, resp, med_book_id):
        """
        Получение медицинской карты с симптомами по идентификатору.
        """
        med_book: dtos.MedicalBookWithSymptoms = (
            self.med_book.get_med_book_with_symptoms(med_book_id)
        )

        resp.media = med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithItemReviews),
        tags=["Medical books with reviews"]
    )
    def on_get_by_id_with_reviews(self, req, resp, med_book_id):
        """
        Получение медицинской карты с отзывами по идентификатору.
        """
        med_book: dtos.MedicalBookWithItemReviews = (
            self.med_book.get_med_book_with_reviews(med_book_id)
        )

        resp.media = med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books with symptoms and reviews"]
    )
    def on_get_by_id_with_symptoms_and_reviews(self, req, resp, med_book_id):
        """
        Получение медицинской карты с симптомами и отзывами по идентификатору.
        """
        med_book: dtos.MedicalBookWithSymptomsAndItemReviews = (
            self.med_book.get_med_book_with_symptoms_and_reviews(med_book_id)
        )

        resp.media = med_book.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewMedicalBookInfo,
        resp=Response(HTTP_201=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_post_new(self, req, resp):
        """
        Создание новой медицинской карты.
        """
        req.media.update(
            {
                'symptom_ids_to_add': req.media['symptom_ids'],
                'item_review_ids_to_add': req.media['item_review_ids']
            }
        )
        new_med_book_info = dtos.NewMedicalBookInfo(**req.media)
        new_med_book: dtos.MedicalBookWithSymptomsAndItemReviews = (
            self.med_book.add(new_med_book_info)
        )

        resp.media = new_med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        json=api_schemas.PutMedicalBookInfo,
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_put_by_id(self, req, resp, med_book_id: int):
        """
        Замена информации на новую в медицинской карте.
        """
        req.media.update({'id': med_book_id})
        updated_med_book_info = dtos.UpdatedMedicalBookInfo(**req.media)
        updated_med_book: dtos.MedicalBookWithSymptomsAndItemReviews = (
            self.med_book.change(updated_med_book_info)
        )

        resp.media = updated_med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        json=api_schemas.PatchMedicalBookInfo,
        resp=Response(HTTP_200=dtos.MedicalBookWithSymptomsAndItemReviews),
        tags=["Medical books"]
    )
    def on_patch_by_id(self, req, resp, med_book_id):
        """
        Изменение или добавление новой информации в медицинскую карту.
        """
        req.media.update({'id': med_book_id})
        new_med_book_info = dtos.MedicalBookInfoToUpdate(**req.media)
        med_book: dtos.MedicalBookWithSymptomsAndItemReviews = (
            self.med_book.change(new_med_book_info)
        )

        resp.media = med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"med_book_id": "Integer"},
        resp=Response(HTTP_200=dtos.MedicalBook),
        tags=["Medical books"]
    )
    def on_delete_by_id(self, req, resp, med_book_id):
        """
        Удаление медицинской карты.
        """
        removed_med_book: dtos.MedicalBook = self.med_book.delete(med_book_id)

        resp.media = removed_med_book.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200
