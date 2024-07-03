import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from kombu import Connection
from kombu.pools import producers

from med_sharing_system.application.interfaces.messaging_queues import (
    QueueMessage,
    Publisher
)
from .scheme import BrokerScheme

# Словарь параметров для продюсера, таких как exchange, routing_key и др.
ProducerParams = Dict[str, Any]
# Функция, которая возвращает параметры для конкретного таргета (очереди или обмена)
ProducerParamsStrategy = Callable[[str], ProducerParams]


@dataclass
class ThreadSafePublisher:
    connection: Connection

    def __post_init__(self):
        self.pool = producers[self.connection]
        self.local = threading.local()

    @property
    def _producer(self):
        if not hasattr(self.local, 'producer'):
            self.local.producer = self.pool.acquire(block=True)
        return self.local.producer

    def release_current(self):
        self._producer.release()
        del self.local.producer

    def publish(self, *args, **kwargs):
        self._producer.publish(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.local, 'producer'):
            self.release_current()


@dataclass
class KombuPublisher(Publisher):
    connection: Connection
    scheme: BrokerScheme
    params_for_target: Optional[ProducerParamsStrategy] = None
    messages_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.thread_safe_publisher = ThreadSafePublisher(connection=self.connection)
        if self.params_for_target is None:
            self.params_for_target = self.params_from_mapping_or_scheme

    def on_finish(self):
        self.thread_safe_publisher.release_current()

    def publish(self, *messages: QueueMessage):
        for message in messages:
            self.thread_safe_publisher.publish(
                message.body, **self.params_for_target(message.target)
            )

    def params_from_mapping(self, target: str) -> ProducerParams:
        return self.messages_params.get(target)

    def params_from_scheme(self, target: str) -> ProducerParams:
        exchange = self.scheme.exchanges[target]
        return dict(exchange=exchange)

    def params_from_mapping_or_scheme(self, target: str) -> ProducerParams:
        params = self.params_from_mapping(target)
        if params:
            return params
        return self.params_from_scheme(target)
