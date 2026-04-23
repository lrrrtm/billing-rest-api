from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")

from testcontainers.postgres import PostgresContainer

ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def configure_environment(postgres_container: PostgresContainer) -> None:
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url(driver="asyncpg")
    os.environ["JWT_SECRET"] = "test-jwt-secret-with-32-chars-min"
    os.environ["WEBHOOK_SECRET"] = "gfdmhghif38yrf9ew0jkf32"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT_DIR,
        env=os.environ.copy(),
        check=True,
    )


@pytest_asyncio.fixture
async def client(configure_environment: None) -> AsyncClient:
    from app.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as async_client:
            yield async_client


@pytest_asyncio.fixture
async def db_session(configure_environment: None):
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def user_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "user12345"},
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin12345"},
    )
    return response.json()["access_token"]
