from falcon import status_codes, HTTP_BAD_REQUEST

from med_sharing_system.application import services
from .. import schemas as api_schemas
from ..spec import spectree


class PatientMatching:
    def __init__(self, patient_matching: services.PatientMatching):
        self.patient_matching = patient_matching

    @spectree.validate(
        json=api_schemas.ClientId,
        tags=["Patient Matching"]
    )
    def on_post(self, req, resp):
        client_id = req.media.get('client_id')
        if client_id:
            self.patient_matching.publish_request_for_search_patients(client_id)
            resp.media = "Request accepted for processing"
            resp.status = status_codes.HTTP_202
        else:
            resp.status = HTTP_BAD_REQUEST
