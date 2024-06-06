from abc import ABC, abstractmethod
from contextlib import ContextDecorator
from dataclasses import dataclass, field

from .message import Message
from .utils import LocalList, ThreadSafeCounter


@dataclass
class Publisher(ContextDecorator, ABC):
    """
    :deferred: Этот атрибут представляет собой потокобезопасный
        список, который хранит сообщения, ожидающие публикации (отложенные) в контексте.
    :calls: Этот потокобезопасный счетчик отслеживает вложенные операторы with,
        чтобы определить, когда происходит выход из самого внешнего контекста.
    """
    deferred: LocalList = field(init=False, default_factory=LocalList)
    calls: ThreadSafeCounter = field(init=False, default_factory=ThreadSafeCounter)

    @abstractmethod
    def publish(self, *messages: Message):
        pass

    def plan(self, *messages: Message):
        self.deferred.extend(messages)

    def flush(self):
        for entity in self.deferred:
            self.publish(entity)
        self.reset()

    def reset(self):
        self.deferred.clear()

    def __enter__(self):
        self.calls.increment()
        return self

    def __exit__(self, *exc):
        self.calls.decrement()
        if self.calls.is_last:
            if exc[0] is None:
                self.flush()
            else:
                self.reset()
        return False
