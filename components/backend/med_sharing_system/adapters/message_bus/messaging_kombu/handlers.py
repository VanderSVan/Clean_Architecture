import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, Dict, Optional

from kombu import Connection, Message

from . import constants
from .publisher import ThreadSafePublisher

MessageBody = Dict[str, Any]


class MessageHandler(ABC):
    @abstractmethod
    def handle(self, message: Message, body: MessageBody):
        pass


@dataclass
class SimpleMessageHandler(MessageHandler):
    """
    Этот обработчик подтверждает сообщение сразу при принятии.
    """
    function: Callable[[Any], Any]

    def __post_init__(self):
        self.logger = logging.getLogger(constants.LOGGER_PREFIX)

    def handle(self, message: Message, body: MessageBody):
        message.ack()
        try:
            self.function(**body)
        except Exception:
            self.logger.exception('Got an error, message have been acked')
            return

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)


@dataclass
class MessageHandlerWithRetries(MessageHandler):
    """
    Этот обработчик отклоняет сообщения при ошибках,
    что позволяет использовать логику повторов.
    При достижении лимита повторов,
    сообщение будет отправлено в "мертвую" очередь.
    """
    function: Callable[[Any], Any]
    error_publisher: ThreadSafePublisher
    max_retry_attempts: int = constants.DEFAULT_ERROR_MAX_RETRY_ATTEMPTS

    def __post_init__(self):
        self.logger = logging.getLogger(constants.LOGGER_PREFIX)

    def _get_attempts_number(self, message: Message) -> Optional[int]:
        if 'x-death' in message.headers:
            headers = message.headers['x-death']
            for header in headers:
                if header['exchange'] == constants.ERROR_RETRY_EXCHANGE:
                    return header['count']
        return None

    def handle(self, message: Message, body: MessageBody):
        try:
            self.function(**body)
        except Exception:
            attempts_number = self._get_attempts_number(message)
            if attempts_number and attempts_number >= self.max_retry_attempts:
                self.logger.exception(
                    'Got an error, all attempts have been exhausted, '
                    'message will be sent to the dead queue'
                )
                with self.error_publisher as publisher:
                    publisher.publish(
                        body=body,
                        exchange=constants.ERROR_DEAD_EXCHANGE,
                        routing_key=message.delivery_info['routing_key'],
                    )
                message.ack()
                return
            self.logger.exception('Got an error, message will be retried')
            message.reject()
            return
        message.ack()

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return id(self) == id(other)


@dataclass
class MessageHandlerFactory:
    connection: Connection

    @cached_property
    def _error_publisher(self) -> ThreadSafePublisher:
        return ThreadSafePublisher(connection=self.connection)

    def create_simple(self, function: Callable[[Any], Any]):
        return SimpleMessageHandler(function=function)

    def create_with_retries(
        self,
        function: Callable[[Any], Any],
        max_retry_attempts: int,
    ):
        return MessageHandlerWithRetries(
            function=function,
            max_retry_attempts=max_retry_attempts,
            error_publisher=self._error_publisher,
        )
