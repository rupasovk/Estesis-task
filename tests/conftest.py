# Нужные библиотеки
import pytest
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from models.dbcontext import *
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import sys
import os

from main import app

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from config import settings

from public.db import get_session

DATABASE_URL_TEST = settings.POSTGRES_DATABASE_URLT
DATABASE_URL_TESTA = settings.POSTGRES_DATABASE_URLTA

engine_test = create_engine(DATABASE_URL_TEST, poolclass=NullPool,  echo=True)
engine_testA = create_async_engine(DATABASE_URL_TESTA, poolclass=NullPool,  echo=True)

async_session_maker = sessionmaker(engine_testA, class_=AsyncSession, expire_on_commit=False)

# создание базы данных
@pytest.fixture(scope="session", autouse=True)
def create_db():
     if not database_exists(engine_test.url):
            create_database(engine_test.url)

# Создание тестовой таблицы
@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
     Base.metadata.drop_all(bind = engine_test)
     Base.metadata.create_all(bind = engine_test)

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio", {"use_uvloop": True}

# Подключение к тестовой БД
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio", {"use_uvloop": True}

@pytest.fixture()
def app():
    from main import app
    yield app

@pytest.fixture()
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client