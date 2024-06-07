from falcon import status_codes
from spectree import Response

from med_sharing_system.application import services, dtos, schemas
from ..spec import spectree


class Symptoms:
    def __init__(self, symptom: services.Symptom):
        self.symptom = symptom

    @spectree.validate(
        query=schemas.FindSymptoms,
        resp=Response(HTTP_200=list[dtos.Symptom]),
        tags=["Symptoms"]
    )
    def on_get(self, req, resp):
        """
        Поиск симптомов.
        """
        filter_params = schemas.FindSymptoms(
            keywords=req.context.query.keywords,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_symptoms: list[dtos.Symptom | None] = (
            self.symptom.find_symptoms(filter_params)
        )

        resp.media = [symptom.dict(exclude_none=True, exclude_unset=True)
                      for symptom in found_symptoms]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"symptom_id": "Integer"},
        resp=Response(HTTP_200=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_get_by_id(self, req, resp, symptom_id: int):
        """
        Получение симптома по его идентификатору.
        """
        symptom: dtos.Symptom = self.symptom.get(symptom_id)

        resp.media = symptom.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewSymptomInfo,
        resp=Response(HTTP_201=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление нового симптома.
        """
        new_symptom_info = dtos.NewSymptomInfo(**req.media)
        new_symptom: dtos.Symptom = self.symptom.add(new_symptom_info)

        resp.media = new_symptom.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"symptom_id": "Integer"},
        json=dtos.NewSymptomInfo,
        resp=Response(HTTP_200=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_put_by_id(self, req, resp, symptom_id: int):
        """
        Изменение информации о симптоме.
        """
        req.media.update({'id': symptom_id})
        new_symptom_info = dtos.Symptom(**req.media)
        updated_symptom: dtos.Symptom = self.symptom.change(new_symptom_info)

        resp.media = updated_symptom.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"symptom_id": "Integer"},
        resp=Response(HTTP_200=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_delete_by_id(self, req, resp, symptom_id):
        """
        Удаление симптома.
        """
        removed_symptom: dtos.Symptom = self.symptom.delete(symptom_id)

        resp.media = removed_symptom.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200
