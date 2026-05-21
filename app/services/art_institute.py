from typing import Optional

import httpx
from cachetools import TTLCache

_cache: TTLCache = TTLCache(maxsize=1000, ttl=300)
_BASE_URL = "https://api.artic.edu/api/v1"
_FIELDS = "id,title,artist_display,date_display,medium_display,place_of_origin"


async def get_artwork(artwork_id: int) -> Optional[dict]:
    if artwork_id in _cache:
        return _cache[artwork_id]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{_BASE_URL}/artworks/{artwork_id}",
            params={"fields": _FIELDS},
        )
        if response.status_code == 404:
            _cache[artwork_id] = None
            return None
        response.raise_for_status()
        data = response.json()["data"]
        _cache[artwork_id] = data
        return data


async def search_artworks(query: str = "", page: int = 1, limit: int = 10) -> dict:
    params: dict = {"page": page, "limit": limit, "fields": _FIELDS}
    if query:
        params["q"] = query
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{_BASE_URL}/artworks/search", params=params)
        response.raise_for_status()
        return response.json()
