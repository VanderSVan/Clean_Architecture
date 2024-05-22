# Установка аргументов
ARG PYTHON_VERSION=3.10
ARG PYTHON_VERSION_SUFFIX=slim

# Создание базового образа с общими переменными среды
FROM python:3.10-slim AS base

# Установка переменных окружения
# Включение обработчика ошибок Python
ENV PYTHONFAULTHANDLER=1 \
    # Отключение буферизации ввода-вывода Python
    PYTHONUNBUFFERED=1 \
    # Случайное значение для хэширования
    PYTHONHASHSEED=random \
    \
    # Настройки pip:
    # Отключение кэширования pip
    PIP_NO_CACHE_DIR=off \
    # Отключение проверки версии pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # Тайм-аут для операций pip
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # Настройки Poetry:
    # Отключение интерактивного режима Poetry
    POETRY_NO_INTERACTION=1 \
    # Отключение создания виртуальных окружений Poetry
    POETRY_VIRTUALENVS_CREATE=false \
    # Директория для кэша Poetry
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    # Директория установки Poetry
    POETRY_HOME='/usr/local' \
    # Версия Poetry
    POETRY_VERSION=1.8.3 \
    # Путь для установки Python зависимостей
    PYSETUP_PATH="/opt/pysetup" \
    # Путь для виртуального окружения
    VENV_PATH="/opt/pysetup/.venv"

# Добавить poetry и venv в PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# ====================================================
FROM base as dependency-installer

# Создание пользователя и группы для запуска приложения
ENV USERNAME=app
RUN groupadd -r $USERNAME && \
    useradd -r -g $USERNAME -d /home/$USERNAME -s /sbin/nologin -c "Docker image user" app

# Установка необходимых системных зависимостей и Poetry
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога и копирование файлов Poetry
WORKDIR $PYSETUP_PATH
COPY ./components/backend/poetry.lock ./components/backend/pyproject.toml ./

# Установка зависимостей проекта без dev-зависимостей и без ANSI-раскраски вывода
RUN poetry install --no-dev --no-ansi && rm -rf $POETRY_CACHE_DIR/*


# ====================================================
FROM dependency-installer as builder

# Установка рабочего каталога и копирование файлов проекта
WORKDIR $PYSETUP_PATH
COPY ./components/backend/ ./

# Сборка проекта в `.whl`
RUN poetry build


# ====================================================
FROM base as tests

# Скопировать и сделать исполняемыми скрипты проекта
COPY ./deployment/backend/entrypoint_*.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint_*.sh

# Установка рабочего каталога и копирование файлов проекта
WORKDIR $PYSETUP_PATH
COPY ./components/backend/ ./

# Копирование установленного `poetry` и зависимостей из стадии `dependency-installer`
COPY --from=dependency-installer $POETRY_HOME $POETRY_HOME
COPY --from=dependency-installer $PYSETUP_PATH $PYSETUP_PATH

# Быстрая установка dev зависимостей, так как не dev уже установлены
# Запуск юнит тестов
RUN poetry install --no-ansi && rm -rf $POETRY_CACHE_DIR/* && pytest -q ./tests/unit


# ====================================================
FROM base as development

# Установка переменной окружения для разработки
ENV API_ENV=development
# Установка рабочего каталога
WORKDIR $PYSETUP_PATH

# Скопировать и сделать исполняемыми скрипты проекта
COPY ./deployment/backend/entrypoint_*.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint_*.sh

# Копирование установленного Poetry и зависимостей из dependency-installer стадии
COPY --from=dependency-installer $POETRY_HOME $POETRY_HOME
COPY --from=dependency-installer $PYSETUP_PATH $PYSETUP_PATH

# Быстрая установка dev зависимостей, так как не dev уже установлены
RUN poetry install --no-ansi && rm -rf $POETRY_CACHE_DIR/*

# Установка рабочего каталога
WORKDIR /app

# Копирование оставшихся файлов, включая test_data.py
COPY ./components/backend ./deployment/backend/test_data.py /app/


# ====================================================
FROM base as production
ENV API_ENV=production
USER $USERNAME

# Скопировать и сделать исполняемыми скрипты проекта
COPY ./deployment/backend/entrypoint_*.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint_*.sh

# Копирование собранного пакета проекта из builder стадии
COPY --from=builder $PYSETUP_PATH/dist /app/dist

# Установка wheel пакета
RUN pip install --upgrade --no-cache-dir pip && \
    pip install /app/dist/*.whl --no-cache-dir

