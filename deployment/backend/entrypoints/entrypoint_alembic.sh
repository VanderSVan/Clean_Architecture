#!/usr/bin/env bash

set -e

if [[ $API_ENV == 'development' ]]; then
  # Выводим значения переменных среды
  echo
  echo "DATABASE_NAME: $DATABASE_NAME"
  echo "DATABASE_HOST: $DATABASE_HOST"
  echo "DATABASE_PORT: $DATABASE_PORT"
  echo "DATABASE_USER: $DATABASE_USER"
  echo "DATABASE_PASSWORD: $DATABASE_PASSWORD"
fi

echo
echo "Waiting for database to start..."
timeout 30 bash -c \
  'while !</dev/tcp/$DATABASE_HOST/$DATABASE_PORT; do sleep 1; done'

echo
echo "Starting alembic migrations..."
python -m simple_medication_selection.launchers.alembic_runner upgrade head
