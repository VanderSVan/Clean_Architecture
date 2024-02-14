from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    DATABASE_NAME: str = Field(..., env='DATABASE_NAME')
    DATABASE_HOST: str = Field(..., env='DATABASE_HOST')
    DATABASE_PORT: int = Field(..., env='DATABASE_PORT')
    DATABASE_USER: str = Field(..., env='DATABASE_USER')
    DATABASE_PASS: str = Field(..., env='DATABASE_PASS')

    # Python путь к каталогу, где лежит запускатор alembic
    # (пример: <project_name>.composites:alembic)
    ALEMBIC_SCRIPT_LOCATION: str = 'adapters.database:alembic'

    # Python путь к каталогу с миграциями
    ALEMBIC_VERSION_LOCATIONS: str = 'adapters.database:migrations'

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

    @property
    def DATABASE_URL(self):
        return 'postgresql+psycopg2://' \
               f'{self.DATABASE_USER}:' \
               f'{self.DATABASE_PASS}@' \
               f'{self.DATABASE_HOST}:' \
               f'{self.DATABASE_PORT}/' \
               f'{self.DATABASE_NAME}'

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

    class Config:
        env_file = Path(__file__).parent.parent.parent.joinpath(".env")
        env_file_encoding = 'utf-8'
