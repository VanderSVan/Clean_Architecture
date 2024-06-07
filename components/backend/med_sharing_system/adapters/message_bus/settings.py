from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    RABBITMQ_HOST: str = Field(..., env='RABBITMQ_HOST')
    RABBITMQ_PORT: int = Field(..., env='RABBITMQ_PORT')
    RABBITMQ_USER: str = Field(..., env='RABBITMQ_USER')
    RABBITMQ_PASSWORD: str = Field(..., env='RABBITMQ_PASSWORD')
    RABBITMQ_VHOST: str = '/'
    LOGGING_LEVEL: str = 'INFO'

    class Config:
        env_file = Path(__file__).parent.parent.parent.parent.joinpath(".env")
        env_file_encoding = 'utf-8'

    @property
    def RABBITMQ_URL(self):
        url = 'amqp://{user}:{password}@{host}:{port}/{vhost}'
        return url.format(
            user=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD,
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,
            vhost=self.RABBITMQ_VHOST,
        )

    @property
    def LOGGING_CONFIG(self):
        return {
            'loggers': {
                'kombu': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False
                }
            }
        }
