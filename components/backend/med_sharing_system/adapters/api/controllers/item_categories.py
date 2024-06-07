from falcon import status_codes
from spectree import Response

from med_sharing_system.application import services, dtos, schemas
from ..spec import spectree


class ItemCategories:
    def __init__(self, item_category: services.ItemCategory):
        self.item_category = item_category

    @spectree.validate(
        query=schemas.FindItemCategories,
        resp=Response(HTTP_200=list[dtos.ItemCategory]),
        tags=["Item Categories"]
    )
    def on_get(self, req, resp):
        """
        Поиск категорий по параметрам.
        """
        filter_params = schemas.FindItemCategories(
            keywords=req.context.query.keywords,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_item_categories: list[dtos.ItemCategory | None] = (
            self.item_category.find(filter_params)
        )

        resp.media = [category.dict(exclude_none=True, exclude_unset=True)
                      for category in found_item_categories]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_category_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemCategory),
        tags=["Item Categories"]
    )
    def on_get_by_id(self, req, resp, category_id):
        """
        Получение информации о категории по его идентификатору.
        """
        category: dtos.ItemCategory = self.item_category.get(category_id)

        resp.media = category.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewItemCategoryInfo,
        resp=Response(HTTP_201=dtos.ItemCategory),
        tags=["Item Categories"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление новой категории.
        """
        new_category_info = dtos.NewItemCategoryInfo(**req.media)
        new_category: dtos.ItemCategory = self.item_category.add(new_category_info)

        resp.media = new_category.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"item_category_id": "Integer"},
        json=dtos.NewItemCategoryInfo,
        resp=Response(HTTP_200=dtos.ItemCategory),
        tags=["Item Categories"]
    )
    def on_put_by_id(self, req, resp, category_id):
        """
        Замена информации о категории на новую.
        """
        req.media.update({'id': category_id})
        updated_category_info = dtos.ItemCategory(**req.media)
        updated_category: dtos.ItemCategory = (
            self.item_category.change(updated_category_info)
        )

        resp.media = updated_category.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"item_category_id": "Integer"},
        resp=Response(HTTP_200=dtos.ItemCategory),
        tags=["Item Categories"]
    )
    def on_delete_by_id(self, req, resp, category_id):
        """
        Удаление категории.
        """
        removed_category: dtos.ItemCategory = self.item_category.delete(category_id)

        resp.media = removed_category.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200
