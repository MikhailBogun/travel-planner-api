from datetime import UTC, datetime, timedelta

import httpx

ARTIC_BASE = "https://api.artic.edu/api/v1"
CACHE_TTL = timedelta(hours=1)

_cache: dict[int, tuple[dict, datetime]] = {}


async def fetch_artwork(artwork_id: int) -> dict | None:
    now = datetime.now(UTC).replace(tzinfo=None)

    if artwork_id in _cache:
        data, cached_at = _cache[artwork_id]
        if now - cached_at < CACHE_TTL:
            return data

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ARTIC_BASE}/artworks/{artwork_id}",
            params={"fields": "id,title"},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()["data"]

    _cache[artwork_id] = (data, now)
    return data
