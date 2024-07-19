# Launchers

**Слой Launchers в гексагональной архитектуре играет ключевую роль в инициализации и запуске приложения.
Этот слой отвечает за сборку и конфигурацию всех компонентов системы, обеспечивая их правильное взаимодействие и функционирование.
Т.е. слой launchers служит точкой входа приложения.**

---
## Навигация по слою
- [Назначение слоя Launchers](#назначение-слоя-launchers)
- [Компоненты слоя Launchers](#компоненты-слоя-launchers)
- [Преимущества изоляции слоя Launchers](#преимущества-изоляции-слоя-launchers)
- [Сложности и потенциальные недостатки](#сложности-и-потенциальные-недостатки)
- [Навигация по backend](../../README.md#навигация-по-backend)

---
## Назначение слоя Launchers
1. **Инициализация компонентов**: Отвечает за создание и настройку всех необходимых объектов и зависимостей.
2. **Внедрение зависимостей**: Обеспечивает правильное связывание различных частей приложения.
3. **Инстанцирование компонентов**: В этом слое создаются все основные компоненты приложения, включая движки, репозитории, сервисы и контроллеры.
4. **Конфигурация приложения**: Загружает и применяет настройки для различных сред выполнения (разработка, тестирование, продакшн).
5. **Оркестрация запуска**: Координирует последовательность запуска различных частей системы.
6. **Управление жизненным циклом**: Контролирует запуск и корректное завершение работы приложения.

[К навигации по слою](#навигация-по-слою)

---
## Компоненты слоя Launchers
### 1. Конфигураторы
- Загрузка настроек из файлов конфигурации, переменных окружения или других источников.
- Применение конфигурации к различным компонентам системы.

### 2. Фабрики
- Создание экземпляров сложных объектов или групп взаимосвязанных объектов.
- Обеспечение правильной инициализации компонентов с необходимыми зависимостями.

### 3. Композиты
- Сборка различных частей приложения в единое целое.
- Обеспечение правильного порядка инициализации и связывания компонентов.

### 4. Скрипты запуска
- Определение точек входа для различных сценариев запуска (веб-сервер, фоновые задачи, миграции и т.д.).
- Обработка аргументов командной строки для кастомизации запуска.

### 5. Менеджеры процессов
- Управление долгоживущими процессами, такими как веб-серверы или воркеры очередей.
- Обеспечение корректного завершения работы и освобождения ресурсов.

[К навигации по слою](#навигация-по-слою)

---
## Преимущества изоляции слоя Launchers
1. **Централизованное управление**: Все аспекты инициализации и конфигурации сосредоточены в одном месте.
2. **Гибкость конфигурации**: Легко адаптировать приложение для работы в различных средах.
3. **Улучшенная тестируемость**: Возможность легко подменять компоненты для тестирования.
4. **Разделение ответственности**: Отделение логики запуска от бизнес-логики и инфраструктурного кода.
5. **Упрощение развертывания**: Стандартизированный подход к запуску упрощает процесс деплоя.

[К навигации по слою](#навигация-по-слою)

---
## Сложности и потенциальные недостатки
1. **Сложность при большом количестве зависимостей**: Может стать сложным при наличии множества взаимосвязанных компонентов.
2. **Потенциальное нарушение принципа DRY**: Возможно дублирование кода инициализации для разных сценариев запуска.
3. **Риск создания "божественного объекта"**: При неправильном проектировании может привести к созданию слишком большого и сложного объекта конфигурации.
4. **Сложность отладки**: Проблемы с инициализацией могут быть труднее диагностировать.
5. **Грязный код**: Как правило, этот слой выглядит нагроможденным и "неопрятным", что усложняет его чтение и понимание.

[К навигации по слою](#навигация-по-слою)