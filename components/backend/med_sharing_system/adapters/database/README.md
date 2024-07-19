# Миграции

1) Прежде чем запустить миграции, необходимо указать корректные данные о
   бд в `.env` файле.
2) Перейди в терминал и убедитесь, что Вы находитесь в корневой директории.
3) Для применения всех существующих миграций, выполните следующую команду:
    ```commandline
    python -m med_sharing_system.launchers.alembic_runner upgrade head
    ```
4) Для возврата на предыдущую миграцию:
    ```commandline
    python -m med_sharing_system.launchers.alembic_runner downgrade -1
    ```
5) Для создания новой миграции:
    ```commandline
   python -m med_sharing_system.launchers.alembic_runner revision --autogenerate -m "first_migration" 
    ```
