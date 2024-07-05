from abc import ABC, abstractmethod

from .. import dtos


class MessageSender(ABC):

    @abstractmethod
    def send(self, message: dtos.Message):
        ...
