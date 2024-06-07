"""
Конфиг gunicorn для запуска API c опцией "-k 'gevent'", но без опции
"--preload". Используй опцию "--config=[путь к файлу конфига]" для передачи
данного конфига gunicorn.

ВАЖНО. Смотри композит api_preload_gevent.py при использовании gunicorn с
опциями "--preload -k 'gevent'" одновременно.
"""
from med_sharing_system.launchers.gevent_settings.db_patch import (
    set_wait_callback
)


def post_fork(server, worker):
    set_wait_callback()
