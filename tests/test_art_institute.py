from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.art_institute import _cache, fetch_artwork


@pytest.fixture(autouse=True)
def clear_cache():
    _cache.clear()
    yield
    _cache.clear()


def make_mock_client(artwork_id: int, title: str):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": {"id": artwork_id, "title": title}}

    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.get = AsyncMock(return_value=response)
    return client


async def test_fetch_artwork_returns_data():
    mock_client = make_mock_client(16568, "Water Lilies")
    with patch("app.services.art_institute.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_artwork(16568)
    assert result == {"id": 16568, "title": "Water Lilies"}


async def test_result_is_cached_on_second_call():
    mock_client = make_mock_client(16568, "Water Lilies")
    with patch("app.services.art_institute.httpx.AsyncClient", return_value=mock_client):
        await fetch_artwork(16568)
        await fetch_artwork(16568)

    assert mock_client.get.call_count == 1
    assert 16568 in _cache


async def test_not_found_returns_none():
    response = MagicMock()
    response.status_code = 404

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=response)

    with patch("app.services.art_institute.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_artwork(99999)

    assert result is None
    assert 99999 not in _cache
