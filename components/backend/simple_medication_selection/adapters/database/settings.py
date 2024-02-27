from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_NAME: str = Field(..., json_schema_extra={'env': 'DATABASE_NAME'})
    DATABASE_HOST: str = Field(..., json_schema_extra={'env': 'DATABASE_HOST'})
    DATABASE_PORT: int = Field(..., json_schema_extra={'env': 'DATABASE_PORT'})
    DATABASE_USER: str = Field(..., json_schema_extra={'env': 'DATABASE_USER'})
    DATABASE_PASS: str = Field(..., json_schema_extra={'env': 'DATABASE_PASS'})

    TEST_DATABASE_NAME: str = Field(None, json_schema_extra={'env': 'TEST_DATABASE_NAME'})
    TEST_DATABASE_HOST: str = Field(None, json_schema_extra={'env': 'TEST_DATABASE_HOST'})
    TEST_DATABASE_PORT: int = Field(None, json_schema_extra={'env': 'TEST_DATABASE_PORT'})
    TEST_DATABASE_USER: str = Field(None, json_schema_extra={'env': 'TEST_DATABASE_USER'})
    TEST_DATABASE_PASS: str = Field(None, json_schema_extra={'env': 'TEST_DATABASE_PASS'})

    # Python путь к каталогу, где лежит запускатор alembic
    # (пример: <project_name>.composites:alembic)
    ALEMBIC_SCRIPT_LOCATION: str = (
        'simple_medication_selection.adapters.database:alembic'
    )

    # Python путь к каталогу с миграциями
    ALEMBIC_VERSION_LOCATIONS: str = (
        'simple_medication_selection.adapters.database:migrations'
    )

    ALEMBIC_MIGRATION_FILENAME_TEMPLATE: str = (
        '%%(year)d_'
        '%%(month).2d_'
        '%%(day).2d_'
        '%%(hour).2d_'
        '%%(minute).2d_'
        '%%(second).2d_'
        '%%(slug)s'
    )

    LOGGING_LEVEL: str = 'INFO'
    SA_LOGS: bool = False

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.joinpath(".env"),
        env_file_encoding='utf-8'
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            'postgresql+psycopg2://'
            f'{self.DATABASE_USER}:'
            f'{self.DATABASE_PASS}@'
            f'{self.DATABASE_HOST}:'
            f'{self.DATABASE_PORT}/'
            f'{self.DATABASE_NAME}'
        )

    @property
    def TEST_DATABASE_URL(self) -> str:
        return (
            'postgresql+psycopg2://'
            f'{self.TEST_DATABASE_USER}:'
            f'{self.TEST_DATABASE_PASS}@'
            f'{self.TEST_DATABASE_HOST}:'
            f'{self.TEST_DATABASE_PORT}/'
            f'{self.TEST_DATABASE_NAME}'
        )

    @property
    def LOGGING_CONFIG(self):
        config = {
            'loggers': {
                'alembic': {
                    'handlers': ['default'],
                    'level': self.LOGGING_LEVEL,
                    'propagate': False
                }
            }
        }

        if self.SA_LOGS:
            config['loggers']['sqlalchemy'] = {
                'handlers': ['default'],
                'level': self.LOGGING_LEVEL,
                'propagate': False
            }

        return config
