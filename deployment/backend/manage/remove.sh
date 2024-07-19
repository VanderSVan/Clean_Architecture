#!/usr/bin/env bash

set -e

cd ../..

set -a
source "$PWD"/components/backend/.env
set +a

cd deployment/backend

case "$1" in
--dev)
  export COMPOSE_PROJECT_NAME=clean-architecture-dev
  echo "The development containers are removing ..."
  docker compose -f docker-compose.dev.yml down
  echo "The development images are removing ..."
  docker rmi \
    clean-architecture-dev-backend \
    clean-architecture-dev-backend_for_tests \
    clean-architecture-dev-match_worker \
    clean-architecture-dev-notification_worker \
    clean-architecture-dev-delivery_consumer
  ;;
*)
  export COMPOSE_PROJECT_NAME=clean-architecture
  echo "The production containers are removing ..."
  docker compose -f docker-compose.prod.yml down
  echo "The production images are removing ..."
  docker rmi \
    clean-architecture-backend \
    clean-architecture-backend_for_tests \
    clean-architecture-match_worker \
    clean-architecture-notification_worker \
    clean-architecture-delivery_consumer
  ;;
esac
