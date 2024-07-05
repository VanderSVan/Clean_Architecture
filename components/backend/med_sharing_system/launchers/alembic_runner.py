import sys

from alembic.config import CommandLine, Config

from med_sharing_system.adapters import database, log


class Settings:
    db = database.Settings()


class Logger:
    log.configure(Settings.db.LOGGING_CONFIG)


def make_config():
    config = Config()
    config.set_main_option(
        'script_location', Settings.db.ALEMBIC_SCRIPT_LOCATION
    )
    config.set_main_option(
        'version_locations', Settings.db.ALEMBIC_VERSION_LOCATIONS
    )
    config.set_main_option('sqlalchemy.url', Settings.db.DATABASE_URL)
    config.set_main_option(
        'file_template', Settings.db.ALEMBIC_MIGRATION_FILENAME_TEMPLATE
    )
    config.set_main_option('timezone', 'UTC')

    return config


def run_cmd(*args):
    log.configure(Settings.db.LOGGING_CONFIG)

    cli = CommandLine()
    cli.run_cmd(make_config(), cli.parser.parse_args(args))


if __name__ == '__main__':
    run_cmd(*sys.argv[1:])
