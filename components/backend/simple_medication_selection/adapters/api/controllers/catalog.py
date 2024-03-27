from typing import Sequence

from falcon import status_codes

from spectree import Response
from ..spec import spectree

from simple_medication_selection.application import services, entities, dtos, schemas


class Catalog:
    def __init__(self, catalog: services.TreatmentItemCatalog):
        self.catalog = catalog

    @spectree.validate(
        path_parameter_descriptions={"item_id": "Integer"},
        resp=Response(HTTP_200=dtos.TreatmentItem),
        tags=["Items"]
    )
    def on_get_by_id(self, req, resp, item_id):
        """
        Получение item по его идентификатору.
        """
        item: dtos.TreatmentItem = self.catalog.get_item(item_id)

        resp.media = item.dict(decode=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_id": "Integer"},
        resp=Response(HTTP_200=dtos.TreatmentItem),
        tags=["Items with reviews"]
    )
    def on_get_by_id_with_reviews(self, req, resp, item_id):
        """
        Получение item по его идентификатору.
        """
        item: entities.TreatmentItem = self.catalog.get_item_with_reviews(item_id)

        resp.media = item.to_dict()
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindTreatmentItems,
        resp=Response(HTTP_200=list[dtos.TreatmentItem]),
        tags=["Items"]
    )
    def on_get(self, req, resp):
        """
        Поиск items по параметрам.
        """
        filter_params = schemas.FindTreatmentItems(
            keywords=req.context.query.keywords,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            min_rating=req.context.query.min_rating,
            max_rating=req.context.query.max_rating,
            min_price=req.context.query.min_price,
            max_price=req.context.query.max_price,
            category_id=req.context.query.category_id,
            type_id=req.context.query.type_id,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_items: list[dtos.TreatmentItem | None] = (
            self.catalog.find_items(filter_params)
        )

        resp.media = [
            item.dict(decode=True) for item in found_items if item is not None
        ]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindTreatmentItems,
        resp=Response(HTTP_200=list[dtos.ItemWithReviews]),
        tags=["Items with reviews"]
    )
    def on_get_with_reviews(self, req, resp):
        """
        Поиск items с отзывами по параметрам.
        """
        filter_params = schemas.FindTreatmentItems(
            keywords=req.context.query.keywords,
            is_helped=req.context.query.is_helped,
            diagnosis_id=req.context.query.diagnosis_id,
            symptom_ids=req.context.query.symptom_ids,
            match_all_symptoms=req.context.query.match_all_symptoms,
            min_rating=req.context.query.min_rating,
            max_rating=req.context.query.max_rating,
            min_price=req.context.query.min_price,
            max_price=req.context.query.max_price,
            category_id=req.context.query.category_id,
            type_id=req.context.query.type_id,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_items: Sequence[entities.TreatmentItem | None] = (
            self.catalog.find_items_with_reviews(filter_params)
        )

        resp.media = [
            item.to_dict() for item in found_items if item is not None
        ]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewItemInfo,
        resp=Response(HTTP_201=dtos.TreatmentItem),
        tags=["Items"]
    )
    def on_post_new(self, req, resp):
        """
        Создание item.
        """
        new_item_info = dtos.NewItemInfo(**req.media)
        new_item: entities.TreatmentItem = self.catalog.add_item(new_item_info)

        resp.media = new_item.to_dict()
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"item_id": "Integer"},
        json=dtos.UpdatedItemInfo,
        resp=Response(HTTP_200=dtos.TreatmentItem),
        tags=["Items"]
    )
    def on_put_by_id(self, req, resp, item_id: int):
        """
        Изменение item.
        """
        req.media.update({'id': item_id})
        updated_item_info = dtos.UpdatedItemInfo(**req.media)
        updated_item: entities.TreatmentItem = self.catalog.change_item(updated_item_info)

        resp.media = updated_item.to_dict()
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_id": "Integer"},
        resp=Response(HTTP_200=dtos.TreatmentItem),
        tags=["Items"]
    )
    def on_delete_by_id(self, req, resp, item_id):
        """
        Удаление item.
        """
        removed_item: entities.TreatmentItem = self.catalog.delete_item(item_id)

        resp.media = removed_item.to_dict()
        resp.status = status_codes.HTTP_200
