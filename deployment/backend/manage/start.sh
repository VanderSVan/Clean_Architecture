#!/usr/bin/env bash

set -e

cd ../..

set -a
source $PWD/components/backend/.env
cd deployment/backend
set +a

case "$1" in
--dev)
  export COMPOSE_PROJECT_NAME=clean-architecture-dev
  echo "The development containers are running ..."
  docker compose -f docker-compose.dev.yml up --build
  pwd
  ;;
*)
  export COMPOSE_PROJECT_NAME=clean-architecture
  echo "The production containers are running ..."
  docker compose -f docker-compose.prod.yml up --build -d
  ;;
esac