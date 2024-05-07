# Readme coming soon

---
### Миграции

1) Прежде чем запустить миграции, необходимо указать корректные данные о 
бд в `.env` файле.
2) Перейди в терминал и убедись, что ты находишься в корневой директории.
3) Для применения всех существующих миграций, выполни следующую команду:
    ```commandline
    python -m simple_medication_selection.launchers.alembic_runner upgrade head
    ```
4) Для возврата на предыдущую миграцию:
    ```commandline
    python -m simple_medication_selection.launchers.alembic_runner downgrade -1
    ```
5) Для создания новой миграции:
    ```commandline
   python -m simple_medication_selection.launchers.alembic_runner revision --autogenerate -m "adding_some_new_code" 
    ```

Запуск в синхронном режиме:
```commandline
gunicorn simple_medication_selection.launchers.api:app
```

Запуск в асинхронном режиме с помощью Gevent:
```commandline
gunicorn -k 'gevent' -w 4 simple_medication_selection.launchers.api:app --config "simple_medication_selection/launchers/gevent_settings/api_gevent_config.py"
```

Запуск в асинхронном режиме с помощью Gevent с предзагрузкой api
```commandline
gunicorn --preload  -k 'gevent' -w 4 simple_medication_selection.launchers.api:app --config "simple_medication_selection/launchers/gevent_settings/api_gevent_config.py"
```