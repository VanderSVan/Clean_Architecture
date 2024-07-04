from .base import Error


class PublisherError(Error):
    message_template = 'Publisher is not initialized or is None.'


class TargetNamesError(Error):
    message_template = 'The name of the publication queues is not specified.'
