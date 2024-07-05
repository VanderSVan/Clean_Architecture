from abc import abstractmethod
from functools import cached_property
from typing import Optional

from amqp import Channel
from kombu import Connection, Exchange, Queue

from . import constants


class BaseBrokerScheme:

    def __init__(self, *queues: Queue):
        self._queues = queues
        self._exchanges = tuple(queue.exchange for queue in self._queues)

    @cached_property
    def exchanges(self):
        return {exchange.name: exchange for exchange in self._exchanges}

    @cached_property
    def queues(self):
        return {queue.name: queue for queue in self._queues}

    def is_durable(self) -> bool:
        return False

    @abstractmethod
    def declare(self, connection: Connection):
        ...


class BrokerScheme(BaseBrokerScheme):

    def declare(self, connection: Connection):
        with connection.channel() as channel:

            for exchange in self._exchanges:
                exchange.declare(channel=channel)

            for queue in self._queues:
                queue.declare(channel=channel)


class BrokerDurableScheme(BaseBrokerScheme):

    def __init__(
        self,
        *queues: Queue,
        retry_ttl_mseconds: Optional[int] = None,
    ):
        super().__init__(*queues)

        if retry_ttl_mseconds:
            assert retry_ttl_mseconds > constants.MIN_ERROR_RETRY_TTL_MSECONDS

            self.retry_ttl_mseconds = retry_ttl_mseconds
        else:
            self.retry_ttl_mseconds = constants.DEFAULT_ERROR_RETRY_TTL_MSECONDS

    @cached_property
    def exchanges(self):
        exchanges = super().exchanges
        error_exchanges = {
            self.dead_exchange.name: self.dead_exchange,
            self.return_exchange.name: self.return_exchange,
            self.retry_exchange.name: self.retry_exchange,
        }

        exchanges.update(error_exchanges)
        return exchanges

    def _check_constraints(self):
        for exchange in self.exchanges.values():
            assert exchange.durable, 'Exchanges should be durable'
            assert not exchange.no_declare, 'Exchanges should be declarable'

        for queue in self._queues:
            assert queue.durable, 'Queues should be durable'
            assert not queue.auto_delete, 'Queues shouldn\'t be auto delete'

    def declare(self, connection: Connection):
        self._check_constraints()

        with connection.channel() as channel:
            for exchange in self.exchanges.values():
                exchange.declare(channel=channel)

            self._declare_error_queues(channel)

            for queue in self._queues:
                self._modify_src_queue_arguments(queue)
                queue.declare(channel=channel)

                queue.bind_to(
                    constants.ERROR_RETURN_EXCHANGE,
                    routing_key=self.create_error_routing_key(queue),
                    channel=channel,
                )

    def _declare_error_queues(self, channel: Channel):
        for retry_queue, dead_queue in self._create_error_queues():
            retry_queue.declare(channel=channel)
            dead_queue.declare(channel=channel)

    def _create_error_queues(self):
        for queue in self._queues:
            retry_queue = self._create_retry_queue(
                queue,
                self.retry_exchange,
                self.return_exchange,
            )

            dead_queue = self._create_dead_queue(queue, self.dead_exchange)

            yield retry_queue, dead_queue

    def _modify_src_queue_arguments(self, src_queue: Queue):
        new_queue_arguments = {
            'x-dead-letter-exchange': constants.ERROR_RETRY_EXCHANGE,
            'x-dead-letter-routing-key': (
                self.create_error_routing_key(src_queue)
            )
        }

        if not src_queue.queue_arguments:
            src_queue.queue_arguments = {}

        src_queue.queue_arguments.update(new_queue_arguments)

    @cached_property
    def dead_exchange(self) -> Exchange:
        return self._create_exchange(constants.ERROR_DEAD_EXCHANGE)

    @cached_property
    def return_exchange(self) -> Exchange:
        return self._create_exchange(constants.ERROR_RETURN_EXCHANGE)

    @cached_property
    def retry_exchange(self) -> Exchange:
        return self._create_exchange(constants.ERROR_RETRY_EXCHANGE)

    def _create_exchange(self, name: str) -> Exchange:
        return Exchange(
            name=name,
            type='direct',
            durable=True,
            no_declare=False,
        )

    def _create_retry_queue(
        self,
        src_queue: Queue,
        retry_exchange: Exchange,
        return_exchange: Exchange,
    ) -> Queue:
        return Queue(
            f'{src_queue.name}{constants.ERROR_RETRY_QUEUE_SUFFIX}',
            retry_exchange,
            routing_key=self.create_error_routing_key(src_queue),
            durable=True,
            auto_delete=False,
            queue_arguments={
                'x-dead-letter-exchange': return_exchange.name,
                'x-dead-letter-routing-key': (
                    self.create_error_routing_key(src_queue)
                ),
                'x-message-ttl': self.retry_ttl_mseconds,
            },
        )

    def _create_dead_queue(
        self,
        src_queue: Queue,
        dead_exchange: Exchange,
    ) -> Queue:
        return Queue(
            f'{src_queue.name}{constants.ERROR_DEAD_QUEUE_SUFFIX}',
            dead_exchange,
            routing_key=self.create_error_routing_key(src_queue),
            durable=True,
            auto_delete=False,
        )

    def create_error_routing_key(self, src_queue: Queue) -> str:
        return f'{constants.ERROR_ROUTING_KEY_PREFIX}{src_queue.name}'

    def is_durable(self) -> bool:
        return True
