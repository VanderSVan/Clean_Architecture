from falcon import status_codes
from spectree import Response

from med_sharing_system.adapters.api import schemas as api_schemas
from med_sharing_system.adapters.api.spec import spectree
from med_sharing_system.application import services, dtos, schemas


class Patients:
    def __init__(self, patient: services.Patient):
        self.patient = patient

    @spectree.validate(
        path_parameter_descriptions={"patient_id": "Integer"},
        resp=Response(HTTP_200=dtos.Patient),
        tags=["Patients"]
    )
    def on_get_by_id(self, req, resp, patient_id):
        """
        Получение пациента по его идентификатору.
        """
        patient: dtos.Patient = self.patient.get(patient_id)

        resp.media = patient.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        query=schemas.FindPatients,
        resp=Response(HTTP_200=list[dtos.Patient]),
        tags=["Patients"]
    )
    def on_get(self, req, resp):
        """
        Поиск пациентов по параметрам.
        """
        filter_params = schemas.FindPatients(
            gender=req.context.query.gender,
            age_from=req.context.query.age_from,
            age_to=req.context.query.age_to,
            skin_type=req.context.query.skin_type,
            sort_field=req.context.query.sort_field,
            sort_direction=req.context.query.sort_direction,
            limit=req.context.query.limit,
            offset=req.context.query.offset
        )
        found_patients: list[dtos.Patient | None] = self.patient.find(filter_params)

        resp.media = [patient.dict(exclude_unset=True, exclude_none=True)
                      for patient in found_patients if patient is not None]
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        json=dtos.NewPatientInfo,
        resp=Response(HTTP_201=dtos.Patient),
        tags=["Patients"]
    )
    def on_post_new(self, req, resp):
        """
        Добавление нового пациента.
        """
        new_patient_info = dtos.NewPatientInfo(**req.media)
        new_patient: dtos.Patient = self.patient.add(new_patient_info)

        resp.media = new_patient.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_201

    @spectree.validate(
        path_parameter_descriptions={"patient_id": "Integer"},
        json=api_schemas.InputUpdatedPatientInfo,
        resp=Response(HTTP_200=dtos.Patient),
        tags=["Patients"]
    )
    def on_put_by_id(self, req, resp, patient_id):
        """
        Изменение информации о пациента.
        """
        req.media.update({'id': patient_id})
        updated_patient_info = dtos.UpdatedPatientInfo(**req.media)
        updated_patient: dtos.Patient = self.patient.change(updated_patient_info)

        resp.media = updated_patient.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200

    @spectree.validate(
        path_parameter_descriptions={"patient_id": "Integer"},
        resp=Response(HTTP_200=dtos.Patient),
        tags=["Patients"]
    )
    def on_delete_by_id(self, req, resp, patient_id):
        """
        Удаление пациента.
        """
        removed_patient: dtos.Patient = self.patient.delete(patient_id)

        resp.media = removed_patient.dict(exclude_unset=True, exclude_none=True)
        resp.status = status_codes.HTTP_200
