import logging
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Iterable

from kombu import Connection
from kombu.mixins import ConsumerMixin

from . import constants
from .handlers import MessageHandler, MessageHandlerFactory
from .scheme import BaseBrokerScheme

AnyCallable = Callable[[Any], None]


@dataclass(kw_only=True)
class KombuConsumer(ConsumerMixin):
    connection: Connection
    scheme: BaseBrokerScheme
    prefetch_count: int = None

    def __post_init__(self):
        self._handlers = defaultdict(list)
        self.message_handler_factory = MessageHandlerFactory(connection=self.connection)
        self.logger = logging.getLogger(constants.LOGGER_PREFIX)

    def _get_queues(self, queue_names: Iterable[str]):
        queues = []
        for name in queue_names:
            assert name in self.scheme.queues, \
                f'Queue with name {name} does not exist in broker scheme!'
            queues.append(self.scheme.queues[name])
        return queues

    def register_handler(self, handler: MessageHandler, *queue_names: str):
        queues = self._get_queues(queue_names)
        self._handlers[handler].extend(queues)

    def register_function(self, function: AnyCallable, *queue_names: str):
        """
        Сообщение подтверждается сразу при принятии.
        """
        handler = self.message_handler_factory.create_simple(function=function)
        queues = self._get_queues(queue_names)
        self._handlers[handler].extend(queues)

    def register_function_with_retries(
        self,
        function: AnyCallable,
        *queue_names: str,
        max_retry_attempts: int = constants.DEFAULT_ERROR_MAX_RETRY_ATTEMPTS,
    ):
        """
        Тут при ошибках в обработке будут повторы и будет передача
        в "мертвую" очередь при достижении максимального числа попыток.
        """
        assert self.scheme.is_durable(), 'Scheme should be durable'
        handler = self.message_handler_factory.create_with_retries(
            function=function,
            max_retry_attempts=max_retry_attempts,
        )
        queues = self._get_queues(queue_names)
        self._handlers[handler].extend(queues)

    def get_consumers(self, consumer_cls, channel):
        consumers = []
        for handler, queues in self._handlers.items():
            on_message = partial(self.on_message, handler=handler)
            c = consumer_cls(
                queues=queues,
                callbacks=[on_message],
                prefetch_count=self.prefetch_count
            )
            consumers.append(c)
        return consumers

    def on_message(self, body, message, handler):
        try:
            self.logger.info('Trying to call: %s', handler)
            handler.handle(message, body)
        except Exception:
            self.logger.exception('Unexpected error occurred')

    def run(self, *args, **kwargs):
        self.logger.info('Worker started')
        return super().run(*args, **kwargs)
