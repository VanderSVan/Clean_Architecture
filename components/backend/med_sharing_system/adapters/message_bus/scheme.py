from kombu import Exchange, Queue

from .messaging_kombu import BrokerScheme

EXCHANGE_TO_MATCHING: str = 'PatientMatching'
EXCHANGE_TO_DELIVERY: str = 'PatientDelivery'

QUEUE_TO_MATCHING: str = 'PatientSearchQueue'
QUEUE_TO_DELIVERY: str = 'PatientsDeliveryQueue'

broker_scheme = BrokerScheme(
    Queue(QUEUE_TO_MATCHING, Exchange(EXCHANGE_TO_MATCHING), max_length=100),
    Queue(QUEUE_TO_DELIVERY, Exchange(EXCHANGE_TO_DELIVERY), max_length=1000),
)
