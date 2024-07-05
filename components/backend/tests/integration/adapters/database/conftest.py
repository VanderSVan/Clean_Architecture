# conftest.py

import pytest
from sqlalchemy import create_engine

from med_sharing_system.adapters.database import (
    Settings,
    metadata,
    TransactionContext,
)


@pytest.fixture(scope="session")
def create_test_db():
    # Создаем базу данных для тестов
    engine = create_engine(Settings().TEST_DATABASE_URL)
    metadata.create_all(bind=engine)

    # Возвращаем URL базы данных для использования в тестах
    yield engine

    # Удаляем тестовую базу данных после выполнения тестов
    metadata.drop_all(bind=engine)


@pytest.fixture(scope='session')
def transaction_context(create_test_db):
    return TransactionContext(bind=create_test_db, expire_on_commit=False)


@pytest.fixture(scope='function')
def session(transaction_context: TransactionContext):
    session = transaction_context.current_session

    if session.in_transaction():
        session.begin_nested()
    else:
        session.begin()

    yield session

    session.rollback()
