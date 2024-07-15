# Clean Architecture

Данный проект предназначен для демонстрации использования таких понятий как 
"Clean architecture", "SOLID", "DDD" и др. на практике.

---
## Запуск проекта

1) Создайте и заполните `components/backend/.env` файл релевантными данными
(пример оформления лежит по пути `components/backend/.env.example`).

2) Для удобства в терминале переместитесь в папку `backend`.
    ```bash
    cd deployment/backend/
    ```
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
Следующие ресурсы доступны при использовании портов указанных в
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
