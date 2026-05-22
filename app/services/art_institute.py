import httpx

ARTIC_BASE = "https://api.artic.edu/api/v1"


async def fetch_artwork(artwork_id: int) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ARTIC_BASE}/artworks/{artwork_id}",
            params={"fields": "id,title"},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["data"]
