#!/usr/bin/env bash

set -e

/usr/bin/entrypoint_alembic.sh

if [ -z "$MED_API_PORT" ]; then
  MED_API_PORT=8000
fi

if [ -z "$ADDITIONAL_API_ARGS" ]; then
  ADDITIONAL_API_ARGS=""
fi

if [ -z "$MED_API_LOG_LEVEL" ]; then
  MED_API_LOG_LEVEL=info
fi

if [ -z "$INSERT_PREPARED_DATA" ]; then
  INSERT_PREPARED_DATA="FALSE"
fi

if [ -z "$API_ENV" ]; then
  API_ENV="production"
fi

if [ -z "$MED_API_ASYNC_MODE" ]; then
  API_ENV="TRUE"
fi

if [ -z "$MED_API_WORKER_COUNT" ]; then
  MED_API_WORKER_COUNT=4
fi

if [ -z "$MED_API_PRELOAD_MODE" ]; then
  MED_API_PRELOAD_MODE="FALSE"
fi

if [[ $INSERT_PREPARED_DATA == 'TRUE' && $API_ENV == 'development' ]]; then
  echo
  echo "Executing test_data.sql..."
  python ./test_data.py
fi

echo
echo "MED_API_PORT: ${MED_API_PORT}"
echo "MED_API_ASYNC_MODE: ${MED_API_ASYNC_MODE}"
echo "MED_API_WORKER_COUNT: ${MED_API_WORKER_COUNT}"
echo "MED_API_PRELOAD_MODE: ${MED_API_PRELOAD_MODE}"
echo "ADDITIONAL_API_ARGS: ${ADDITIONAL_API_ARGS}"
echo "MED_API_LOG_LEVEL: ${MED_API_LOG_LEVEL}"
echo

# shellcheck disable=SC2089
GUNICORN_CMD_ARGS="--bind=0.0.0.0:${MED_API_PORT} --log-level=${MED_API_LOG_LEVEL} --workers=4 --error-logfile=- --access-logfile=- --forwarded-allow-ip='*' --proxy-allow-from='*' ${ADDITIONAL_API_ARGS} -t 1200 --preload"
# shellcheck disable=SC2090
export GUNICORN_CMD_ARGS

if [[ $MED_API_ASYNC_MODE == 'TRUE' && $MED_API_PRELOAD_MODE == 'TRUE' ]]; then
  gunicorn --preload -k 'gevent' -w "${MED_API_WORKER_COUNT}" med_sharing_system.launchers.api_with_rabbitmq:app --config "med_sharing_system/launchers/gevent_settings/api_gevent_config.py"
elif [[ $MED_API_ASYNC_MODE == 'TRUE' ]]; then
  gunicorn -k 'gevent' -w "${MED_API_WORKER_COUNT}" med_sharing_system.launchers.api_with_rabbitmq:app --config "med_sharing_system/launchers/gevent_settings/api_gevent_config.py"
else
  gunicorn med_sharing_system.launchers.api:app
fi
