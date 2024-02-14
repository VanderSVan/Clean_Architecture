# Readme coming soon

---
### Виртуального окружения
<details>
<summary>Создание виртуального окружения</summary>

1) Перейди в необходимую директорию и выполни команду:
```commandline
python -m venv venv
```
2) Для `linux` скопируй файл `pip.conf` во внутрь папки `venv`. <br>
Для `windows` скопируй файл `pip.conf` во внутрь папки `venv` и переименуй в `pip.ini`.
3) Далее выполни следующую команду:
   - Если Linux
    ```commandline
    source venv/bin/activate
    ```
   - Eсли Windows
    ```commandline
    venv\Scripts\activate.bat
    ```
4) Выполни следующую команду:
   - Если необходимо установить только prod зависимости
    ```commandline
    pip install .
    ```
   - Если необходимо установить не только prod зависимости, но и dev
    ```commandline
    pip install -e .[dev]
    ```
</details>

---

### Линтеры
<details>
<summary>isort</summary>

### isort
Если необходимо пропустить какую-то директорию,
то добавь следующую строчку в `pyproject.toml` в разделе `isort`:
```toml
[tool.isort]
skip_glob = ["your/path/to/file/or/directory"]
```
Пример:

```toml
[tool.isort]
profile = "black"
known_first_party = "ml_core"
known_evraz = "evraz"
sections=["FUTURE", "STDLIB", "THIRDPARTY", "EVRAZ", "FIRSTPARTY", "LOCALFOLDER"]
line_length = 80
skip_glob = ["advisor_core/application/advisor_core/core"]
```
Затем запусти команду:
```commandline
isort .
```
</details>

<details>
<summary>yapf</summary>

### yapf
Если необходимо пропустить какую-то директорию,
то добавь следующуй аргумент `-e` в команде:

```commandline
yapf -ir your/direcory -e your/exclude/directory
```
Примеры:
```commandline
yapf -ir advisor_core -e advisor_core/application/advisor_core/core/
```

```commandline
yapf -ir . -e advisor_core/application/advice/configs
```
</details>

<details>
<summary>flake8</summary>

### flake8
Если необходимо пропустить какую-то директорию,
то добавь следующуй аргумент `--exclude` в команде:

```commandline
flake8 your/direcory --exclude=your/exclude/directory
```
Пример:
```commandline
flake8 advisor_core --exclude=advisor_core/application/advisor_core/core/
```
</details>

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


