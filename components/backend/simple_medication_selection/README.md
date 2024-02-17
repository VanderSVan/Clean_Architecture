# Readme coming soon

---
### Миграции

1) Прежде чем запустить миграции, необходимо указать корректные данные о 
бд в `.env` файле.
2) Перейди в терминал и убедись, что ты находишься в корневой директории.
3) Для применения всех существующих миграций, выполни следующую команду:
    ```commandline
    python -m entrypoints.alembic_runner upgrade head
    ```
4) Для возврата на предыдущую миграцию:
    ```commandline
    python -m entrypoints.alembic_runner downgrade -1
    ```
5) Для создания новой миграции:
    ```commandline
    python -m entrypoints.alembic_runner revision --autogenerate -m "adding_some_new_code"
    ```


