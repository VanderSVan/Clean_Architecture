import logging.config

from .settings import Settings


def configure(*configs: dict) -> None:
    result_config = Settings().LOGGING_CONFIG

    for config in configs:
        result_config['formatters'].update(config.get('formatters', {}))
        result_config['handlers'].update(config.get('handlers', {}))
        result_config['loggers'].update(config.get('loggers', {}))

    logging.config.dictConfig(result_config)
