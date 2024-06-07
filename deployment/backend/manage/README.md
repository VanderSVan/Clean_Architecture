# Директория управления проектом

1) **start.sh** - для запуска контейнеров проекта с помощью команд docker-compose (флаг `--dev` опционален).
2) **restart.sh** - для перезапуска контейнеров проекта с помощью команд docker-compose (флаг `--dev` опционален).
3) **stop.sh** - для остановки контейнеров проекта с помощью команд docker-compose (флаг `--dev` опционален).
4) **remove.sh** - для удаления контейнеров проекта с помощью команд docker-compose (флаг `--dev` опционален).

Флаг `--dev` необходим для управления контейнерами разработки.
Для production версии вызываем команды без флагов.

## КОМАНДЫ:

```commandline
bash start.sh --dev
```

```commandline
bash restart.sh --dev
```

```commandline
bash stop.sh --dev
```

```commandline
bash remove.sh --dev
```