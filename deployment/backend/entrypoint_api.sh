#!/usr/bin/env bash

set -e

/usr/bin/entrypoint_alembic.sh

if [ -z "$API_PORT" ]; then
  API_PORT=8000
fi

if [ -z "$ADDITIONAL_API_ARGS" ]; then
  ADDITIONAL_API_ARGS=""
fi

if [ -z "$API_LOG_LEVEL" ]; then
  API_LOG_LEVEL=info
fi

if [ -z "$INSERT_PREPARED_DATA" ]; then
  INSERT_PREPARED_DATA="FALSE"
fi

if [ -z "$API_ENV" ]; then
  API_ENV="production"
fi

if [[ $INSERT_PREPARED_DATA == 'TRUE' && $API_ENV == 'development' ]]; then
  echo
  echo "Executing test_data.sql..."
  python ./test_data.py
fi

echo
echo "API_PORT: ${API_PORT}"
echo "ADDITIONAL_API_ARGS: ${ADDITIONAL_API_ARGS}"
echo "API_LOG_LEVEL: ${API_LOG_LEVEL}"
echo

# shellcheck disable=SC2089
GUNICORN_CMD_ARGS="--bind=0.0.0.0:${API_PORT} --log-level=${API_LOG_LEVEL} --workers=4 --error-logfile=- --access-logfile=- --forwarded-allow-ip='*' --proxy-allow-from='*' ${ADDITIONAL_API_ARGS} -t 1200 --preload"
# shellcheck disable=SC2090
export GUNICORN_CMD_ARGS

gunicorn simple_medication_selection.launchers.api:app
