from kombu import Exchange, Queue

from .messaging_kombu import BrokerScheme

broker_scheme = BrokerScheme(
    Queue('PatientsMatchedQueue', Exchange('PatientMatching'), max_length=10)
)
