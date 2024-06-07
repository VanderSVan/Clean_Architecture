# Пакет для работы с очередями сообщений на основе Kombu

Этот пакет предоставляет инфраструктуру для обработки и потребления сообщений с использованием библиотеки Kombu. Kombu - это библиотека для Python, предоставляющая высокоуровневый интерфейс для управления системами обмена сообщениями. Этот пакет предназначен для работы с брокерами сообщений, такими как RabbitMQ, и предоставляет различные обработчики и публикации для эффективного управления обработкой сообщений.

## Содержание

- [Использование](#использование)
  - [Создание схемы](#создание-схемы)
  - [Создание потребителя](#создание-потребителя)
  - [Регистрация обработчиков](#регистрация-обработчиков)
  - [Публикация сообщений](#публикация-сообщений)
- [Компоненты](#компоненты)
  - [KombuConsumer](#kombuconsumer)
  - [MessageHandlerFactory](#messagehandlerfactory)
  - [ThreadSafePublisher](#threadsafepublisher)
  - [BrokerScheme](#brokerscheme)
  - [Константы](#константы)

## Использование

### Создание схемы

Сначала определите схему брокера, включая очереди и обменники, которые вы будете использовать.

```python
from kombu import Exchange, Queue
from messaging_kombu.scheme import BrokerScheme

exchange = Exchange('default_exchange', type='direct')
queues = (
    Queue('queue1', exchange, routing_key='key1'),
    Queue('queue2', exchange, routing_key='key2'),
)

scheme = BrokerScheme(queues=queues)
```

### Создание потребителя

Затем создайте потребителя, который будет использовать схему.

```python
from kombu import Connection
from messaging_kombu.consumer import KombuConsumer

connection = Connection('amqp://guest:guest@localhost:5672//')
consumer = KombuConsumer(connection=connection, scheme=scheme, prefetch_count=10)
```

### Регистрация обработчиков

Зарегистрируйте обработчики для обработки сообщений из определённых очередей.

```python
from messaging_kombu.handlers import MessageHandlerFactory

def simple_handler_function(body):
    print(f"Обработка сообщения: {body}")

factory = MessageHandlerFactory(connection)
simple_handler = factory.create_simple(function=simple_handler_function)
consumer.register_handler(simple_handler, 'queue1')

# С повторами
def retry_handler_function(body):
    if some_condition_not_met(body):
        raise Exception("Повторная обработка сообщения")

retry_handler = factory.create_with_retries(function=retry_handler_function, max_retry_attempts=3)
consumer.register_handler(retry_handler, 'queue2')
```

### Запуск потребителя

Запустите потребителя для начала обработки сообщений.

```python
consumer.run()
```

### Публикация сообщений

Публикуйте сообщения в определённые обменники и очереди.

```python
from messaging_kombu.publisher import KombuPublisher

publisher = KombuPublisher(connection=connection, scheme=scheme)

message = {
    'body': 'Привет, мир!',
    'target': 'queue1'
}

publisher.publish(message)
```

## Компоненты

### KombuConsumer

`KombuConsumer` - это класс потребителя, расширяющий `ConsumerMixin` из Kombu. Он управляет подключением и схемой, а также предоставляет методы для регистрации обработчиков сообщений и функций.

### MessageHandlerFactory

`MessageHandlerFactory` создает различные типы обработчиков сообщений. Он поддерживает простые обработчики, которые подтверждают сообщения сразу, и обработчики с логикой повторов, которые управляют повторной доставкой сообщений при сбоях.

### ThreadSafePublisher

`ThreadSafePublisher` обеспечивает потокобезопасную публикацию сообщений в брокер. Он управляет пулом производителей и позволяет эффективно публиковать сообщения в многопоточной среде.

### BrokerScheme

`BrokerScheme` определяет топологию обмена сообщениями, включая обменники и очереди. Он поддерживает долговечные и недолговечные конфигурации и предоставляет методы для объявления сущностей обмена сообщениями в брокере.

### Константы

`constants.py` содержит различные конфигурационные константы, используемые по всему пакету, такие как префиксы для логгера и количество попыток повторов по умолчанию.
