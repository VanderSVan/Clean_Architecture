from falcon import status_codes
from spectree import Response

from med_sharing_system.application import services, dtos, schemas
from ..spec import spectree


class ItemTypes:
    def __init__(self, item_type: services.ItemType):
        self.item_type = item_type

    @spectree.validate(
        query=schemas.FindItemTypes,
        resp=Response(HTTP_200=list[dtos.ItemType]),
        tags=["Item Types"]
    )
    def on_get(self, req, resp):
        """
        Поиск типы items по параметрам.
        """
        filter_params = schemas.FindItemTypes(
            keywords=req.context.query.keywords,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_item_types: list[dtos.ItemType | None] = (
            self.item_type.find(filter_params)
        )

        resp.media = [item_type.dict(exclude_none=True, exclude_unset=True)
                      for item_type in found_item_types]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_type_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemType),
        tags=["Item Types"]
    )
    def on_get_by_id(self, req, resp, type_id):
        """
        Получение информации о типе item по его идентификатору.
        """
        item_type: dtos.ItemType = self.item_type.get(type_id)

        resp.media = item_type.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewItemTypeInfo,
        resp=Response(HTTP_201=dtos.ItemType),
        tags=["Item Types"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление нового типа для items.
        """
        new_item_type_info = dtos.NewItemTypeInfo(**req.media)
        new_item_type: dtos.ItemType = self.item_type.add(new_item_type_info)

        resp.media = new_item_type.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"item_type_id": "Integer"},
        json=dtos.NewItemTypeInfo,
        resp=Response(HTTP_200=dtos.ItemType),
        tags=["Item Types"]
    )
    def on_put_by_id(self, req, resp, type_id):
        """
        Замена информации о типе item на новую.
        """
        req.media.update({'id': type_id})
        updated_item_type_info = dtos.ItemType(**req.media)
        updated_item_type: dtos.ItemType = (
            self.item_type.change(updated_item_type_info)
        )

        resp.media = updated_item_type.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_type_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemType),
        tags=["Item Types"]
    )
    def on_delete_by_id(self, req, resp, type_id):
        """
        Удаление типа items.
        """
        removed_item_type: dtos.ItemType = self.item_type.delete(type_id)

        resp.media = removed_item_type.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200
