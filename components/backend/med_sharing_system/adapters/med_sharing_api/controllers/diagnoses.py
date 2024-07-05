from falcon import status_codes
from spectree import Response

from med_sharing_system.application import services, dtos, schemas
from ..spec import spectree


class Diagnoses:
    def __init__(self, diagnosis: services.Diagnosis):
        self.diagnosis = diagnosis

    @spectree.validate(
        query=schemas.FindDiagnoses,
        resp=Response(HTTP_200=list[dtos.Diagnosis]),
        tags=["Diagnoses"]
    )
    def on_get(self, req, resp):
        """
        Поиск диагнозов по параметрам.
        """
        filter_params = schemas.FindDiagnoses(
            keywords=req.context.query.keywords,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_diagnoses: list[dtos.Diagnosis | None] = self.diagnosis.find(filter_params)

        resp.media = [diagnosis.dict(exclude_none=True, exclude_unset=True)
                      for diagnosis in found_diagnoses]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"diagnosis_id": "Integer"},
        resp=Response(HTTP_200=dtos.Diagnosis),
        tags=["Diagnoses"]
    )
    def on_get_by_id(self, req, resp, diagnosis_id):
        """
        Получение информации о диагнозе по его идентификатору.
        """
        diagnosis: dtos.Diagnosis = self.diagnosis.get(diagnosis_id)

        resp.media = diagnosis.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewDiagnosisInfo,
        resp=Response(HTTP_201=dtos.Diagnosis),
        tags=["Diagnoses"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление нового диагноза.
        """
        new_diagnosis_info = dtos.NewDiagnosisInfo(**req.media)
        new_diagnosis: dtos.Diagnosis = self.diagnosis.add(new_diagnosis_info)

        resp.media = new_diagnosis.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"diagnosis_id": "Integer"},
        json=dtos.NewDiagnosisInfo,
        resp=Response(HTTP_200=dtos.Diagnosis),
        tags=["Diagnoses"]
    )
    def on_put_by_id(self, req, resp, diagnosis_id):
        """
        Замена информации о диагнозе на новую.
        """
        req.media.update({'id': diagnosis_id})
        updated_diagnosis_info = dtos.Diagnosis(**req.media)
        updated_diagnosis: dtos.Diagnosis = self.diagnosis.change(updated_diagnosis_info)

        resp.media = updated_diagnosis.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"diagnosis_id": "Integer"},
        resp=Response(HTTP_200=dtos.Diagnosis),
        tags=["Diagnoses"]
    )
    def on_delete_by_id(self, req, resp, diagnosis_id):
        """
        Удаление диагноза.
        """
        removed_diagnosis: dtos.Diagnosis = self.diagnosis.delete(diagnosis_id)

        resp.media = removed_diagnosis.dict(exclude_none=True, exclude_unset=True)
        resp.status = status_codes.HTTP_200
