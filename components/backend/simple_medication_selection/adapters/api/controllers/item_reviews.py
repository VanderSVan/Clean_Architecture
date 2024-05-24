from dataclasses import asdict

from falcon import status_codes
from spectree import Response

from simple_medication_selection.application import services, entities, dtos, schemas
from simple_medication_selection.adapters.api.spec import spectree


class ItemReviews:
    def __init__(self, item_review: services.ItemReview) -> None:
        self.review = item_review

    @spectree.validate(
        path_parameter_descriptions={"review_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemReview),
        tags=["Reviews"]
    )
    def on_get_by_id(self, req, resp, review_id):
        """
        Получение отзыва по его идентификатору.
        """
        review: dtos.ItemReview = self.review.get_review(review_id)

        resp.media = review.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindItemReviews,
        resp=Response(HTTP_200=list[dtos.ItemReview]),
        tags=["Reviews"]
    )
    def on_get(self, req, resp):
        """
        Поиск отзывов по параметрам.
        """
        filter_params = schemas.FindItemReviews(
            item_ids=req.context.query.item_ids,
            patient_id=req.context.query.patient_id,
            is_helped=req.context.query.is_helped,
            min_rating=req.context.query.min_rating,
            max_rating=req.context.query.max_rating,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset,
            exclude_review_fields=req.context.query.exclude_review_fields
        )
        found_reviews: list[dtos.ItemReview | None] = (
            self.review.find_reviews(filter_params)
        )
        resp.media = [review.dict(exclude_none=True, exclude_unset=True)
                      for review in found_reviews if review is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewItemReviewInfo,
        resp=Response(HTTP_201=dtos.ItemReview),
        tags=["Reviews"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление нового отзыва.
        """
        new_review_info = dtos.NewItemReviewInfo(**req.media)
        new_review: dtos.ItemReview = self.review.add(new_review_info)

        resp.media = new_review.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"review_id": "Integer"},
        json=dtos.UpdatedItemReviewInfo,
        resp=Response(HTTP_200=dtos.ItemReview),
        tags=["Reviews"]
    )
    def on_put_by_id(self, req, resp, review_id):
        """
        Изменение отзыва.
        """
        req.media.update({'id': review_id})
        updated_review_info = dtos.UpdatedItemReviewInfo(**req.media)
        updated_review: dtos.ItemReview = self.review.change(updated_review_info)

        resp.media = updated_review.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"review_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemReview),
        tags=["Reviews"]
    )
    def on_delete_by_id(self, req, resp, review_id):
        """
        Удаление отзыва.
        """
        removed_review: dtos.ItemReview = self.review.delete(review_id)

        resp.media = removed_review.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200
