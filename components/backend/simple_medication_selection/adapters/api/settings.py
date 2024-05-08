from pathlib import Path

from pydantic import BaseSettings, Field


class SwaggerSettings(BaseSettings):
    ON: bool = False
    TITLE: str = 'Simple Medication Selection API'
    PATH: str = 'apidoc'
    FILENAME: str = 'openapi.json'
    SERVERS: list[tuple[str, str]] = Field(default_factory=list)

    class Config:
        env_prefix = 'SWAGGER_'
        env_file = Path(__file__).parent.parent.parent.parent.joinpath(".env")
        print(f"{env_file=}")
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    API_VERSION: str = 'v1'
    API_PREFIX: str = f'/api/{API_VERSION}'

    SWAGGER: SwaggerSettings = Field(default_factory=SwaggerSettings)

    ALLOW_ORIGINS: str | tuple[str, ...] = Field(default_factory=tuple)

    LOGGING_LEVEL: str = 'DEBUG'

    @property
    def LOGGING_CONFIG(self) -> dict:
        return {
            'loggers': {
                'gunicorn': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False
                },
                'spectree': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False
                }
            }
        }
