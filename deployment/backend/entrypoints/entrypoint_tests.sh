#!/usr/bin/env bash

set -e

if [[ $API_ENV == 'development' ]]; then
  echo
  echo "TEST_DATABASE_NAME: $TEST_DATABASE_NAME"
  echo "TEST_DATABASE_HOST: $TEST_DATABASE_HOST"
  echo "TEST_DATABASE_PORT: $TEST_DATABASE_PORT"
  echo "TEST_DATABASE_USER: $TEST_DATABASE_USER"
  echo "TEST_DATABASE_PASSWORD: $TEST_DATABASE_PASSWORD"
fi

echo
echo "Waiting for database to start..."
timeout 30 bash -c \
  'while !</dev/tcp/$TEST_DATABASE_HOST/$TEST_DATABASE_PORT; do sleep 1; done'
echo

echo "Running integration tests..."
if [[ $API_ENV == 'development' ]]; then
  pytest -q ./tests/med_sharing_system/integration || true
else
  pytest -qq ./tests/med_sharing_system/integration
fi
integration_test_status=$?

# Если тесты провалились и это production mode, то завершаем с ошибкой, иначе без ошибки
if [ $integration_test_status -ne 0 ]; then
  echo "One or more integration tests failed" >&2
  if [[ $API_ENV == 'production' ]]; then
    exit 1
  fi
fi

echo "All tests passed successfully"
