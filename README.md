# Clean Architecture

Данный проект предназначен для демонстрации использования таких понятий как 
"Clean architecture", "SOLID", "DDD" и др. на практике.

---
## Project stack:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Falcon](https://img.shields.io/badge/Falcon-505050?style=for-the-badge&logo=falcon)
![Gevent](https://img.shields.io/badge/Gevent-228B22?style=for-the-badge&logo=gevent)
![Websockets](https://img.shields.io/badge/Websockets-1E5945.svg?style=for-the-badge&logo=websockets)
![Pydantic](https://img.shields.io/badge/Pydantic-ff43a1.svg?style=for-the-badge&logo=pydantic)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-7a1b0c.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/alembic-1E5945.svg?style=for-the-badge&logo=alembic)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Kombu](https://img.shields.io/badge/Kombu-4B0082?style=for-the-badge&logo=kombu)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-%23FF6347.svg?style=for-the-badge&logo=rabbitMQ&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23990024.svg?style=for-the-badge&logo=redis&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-003153.svg?style=for-the-badge&logo=pytest&logoColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Docker-compose](https://img.shields.io/badge/docker--compose-6495ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

---
## Запуск проекта

1) Создайте и заполните файл `components/backend/.env` релевантными данными
(пример оформления лежит по пути `components/backend/.env.example`).

2) Для удобства в терминале переместитесь в папку `deployment/backend/`.

3) Запустите проект используя следующие команды:  
    Доступны 2 вариации управления развертыванием проекта **development** и **production**.
    
    <details>
    <summary>Production команды:</summary>
    
    ```bash
    bash ./manage/start.sh
    ```
    
    ```bash
    bash ./manage/restart.sh
    ```
    
    ```bash
    bash ./manage/stop.sh
    ```
    
    ```bash
    bash ./manage/remove.sh
    ```
    </details>
    
    <details>
    <summary>Development команды:</summary>
    
    ```bash
    bash ./manage/start.sh --dev
    ```
    
    ```bash
    bash ./manage/restart.sh --dev
    ```
    
    ```bash
    bash ./manage/stop.sh --dev
    ```
    
    ```bash
    bash ./manage/remove.sh --dev
    ```
    </details>
    
    Подробнее в [директории управление проектом](deployment/backend/manage/README.md).

---
## Доступные ресурсы проекта:
Следующие ресурсы доступны при использовании портов по умолчанию, указанных в
`components/backend/.env.example`.
<details>
<summary>Production ресурсы:</summary>

1) Api:  
http://0.0.0.0:8080/api/v1
2) WebSocket Notifications:  
http://0.0.0.0:8080/api/v1/
3) Pgadmin:  
http://0.0.0.0:8080/pgadmin4/

</details>

<details>
<summary>Development ресурсы:</summary>

1) Api:  
http://0.0.0.0:9000/api/v1 - напрямую,  
http://0.0.0.0:8080/api/v1 - через nginx  
2) WebSocket Notifications:  
http://0.0.0.0:9000/api/v1/ - напрямую,  
http://0.0.0.0:8080/api/v1/ - через nginx
3) Swagger:  
http://0.0.0.0:9000/apidoc/swagger - напрямую,  
http://0.0.0.0:8080/apidoc/swagger - через nginx  
4) Redoc:  
http://0.0.0.0:9000/apidoc/redoc - напрямую,  
http://0.0.0.0:8080/apidoc/redoc - через nginx  
5) Pgadmin:  
http://0.0.0.0:5050/ - напрямую,  
http://0.0.0.0:8080/pgadmin4/ - через nginx
6) Web rabbitmq:  
http://0.0.0.0:15672/ - напрямую
</details>
