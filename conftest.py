import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import app.models  # noqa: E402, F401 — registers all models with SQLModel.metadata
from app.auth import verify_credentials  # noqa: E402
from app.database import get_session  # noqa: E402
from main import app  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def session():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(session):
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[verify_credentials] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def raw_client(session):
    """Client that does not bypass auth — for testing authentication behaviour."""
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_artwork():
    with patch(
        "app.services.project_service.fetch_artwork", new_callable=AsyncMock
    ) as mock:
        mock.return_value = {"id": 16568, "title": "Water Lilies"}
        yield mock


@pytest.fixture
def mock_artwork_not_found():
    with patch(
        "app.services.project_service.fetch_artwork", new_callable=AsyncMock
    ) as mock:
        mock.return_value = None
        yield mock
