from falcon import status_codes

from med_sharing_system.application import services
from ..spec import spectree


class PatientMatching:
    def __init__(self, patient_matching: services.PatientMatching):
        self.patient_matching = patient_matching

    @spectree.validate(
        tags=["Patient Matching"]
    )
    def on_get(self, req, resp):
        self.patient_matching.find_matching_patient()
        resp.media = "Request accepted for processing"
        resp.status = status_codes.HTTP_202
