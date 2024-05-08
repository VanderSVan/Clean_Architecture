# Добавьте зависимость gevent в setup.cfg вашего проекта
import gevent.monkey

# gevent патчинг необходим когда мы используем gunicorn с опциями
# "--preload -k 'gevent'". Это потому, что если мы используем опцию "--preload",
# gunicorn запускает gevent патчинг уже после загрузки композита API
gevent.monkey.patch_all()

# Патчим подключение к БД
from simple_medication_selection.launchers.gevent_settings.db_patch import (
    set_wait_callback
)

set_wait_callback()

from simple_medication_selection.launchers.api import app

__all__ = [
    'app',
]
