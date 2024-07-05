import logging
from dataclasses import dataclass

import requests

from med_sharing_system.application import interfaces, dtos


@dataclass
class WebsocketNotifier(interfaces.MessageSender):
    url: str
    logger: logging.Logger | None = None

    def __post_init__(self):
        if self.logger is None:
            self.logger = logging.getLogger(self.__class__.__name__)

    def send(self, message: dtos.Message) -> None:
        target = message.target
        title = message.title
        body = message.body

        self.logger.info(
            'Sending message to {%s}\n'
            'Title: {%s}\n'
            'Body: {%s}\n',
            target, title, body
        )

        requests.post(self.url, json={'body': body, 'target': target})
