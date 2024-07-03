from kombu import Exchange, Queue

from .messaging_kombu import BrokerScheme

broker_scheme = BrokerScheme(
    Queue('PatientSearchQueue', Exchange('PatientMatching'), max_length=50),
    Queue('PatientsDeliveryQueue', Exchange('PatientDelivery'), max_length=10),
)
