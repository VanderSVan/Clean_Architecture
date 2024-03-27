from dataclasses import asdict
from typing import Sequence

from falcon import status_codes

from spectree import Response
from ..spec import spectree

from simple_medication_selection.application import services, entities, dtos, schemas


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
        found_symptoms: Sequence[entities.Symptom | None] = (
            self.symptom.find_symptoms(filter_params)
        )

        resp.media = [asdict(symptom) for symptom in found_symptoms]
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
        symptom: entities.Symptom = self.symptom.get(symptom_id)

        resp.media = asdict(symptom)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewSymptomInfo,
        resp=Response(HTTP_201=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_post_new(self, req, resp):
        """
        Создание симптома.
        """
        new_symptom_info = dtos.NewSymptomInfo(**req.media)
        new_symptom: entities.Symptom = self.symptom.create(new_symptom_info)

        resp.media = asdict(new_symptom)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"symptom_id": "Integer"},
        json=dtos.NewSymptomInfo,
        resp=Response(HTTP_200=dtos.Symptom),
        tags=["Symptoms"]
    )
    def on_put_by_id(self, req, resp, symptom_id: int):
        """
        Изменение симптома.
        """
        req.media.update({'id': symptom_id})
        new_symptom_info = dtos.Symptom(**req.media)
        updated_symptom: entities.Symptom = self.symptom.change(new_symptom_info)

        resp.media = asdict(updated_symptom)
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
        removed_symptom: entities.Symptom = self.symptom.delete(symptom_id)

        resp.media = asdict(removed_symptom)
        resp.status = status_codes.HTTP_200
        