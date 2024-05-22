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
   python -m simple_medication_selection.launchers.alembic_runner revision --autogenerate -m "first_migration" 
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
Доступно на dev:
http://0.0.0.0:9000/api/v1 - напрямую,
http://0.0.0.0:8080/api/v1 - через nginx

http://0.0.0.0:9000/apidoc/swagger - напрямую,
http://0.0.0.0:8080/apidoc/swagger - через nginx

http://0.0.0.0:9000/apidoc/redoc - напрямую,
http://0.0.0.0:8080/apidoc/redoc - через nginx

http://0.0.0.0:5050/ - напрямую,
http://0.0.0.0:8080/pgadmin4/ - через nginx

Доступно на prod (только nginx):
http://0.0.0.0:8080/api/v1/diagnoses ,
http://0.0.0.0:8080/pgadmin4/

```commandline
poetry export --without-hashes --format=requirements.txt > requirements.txt
```