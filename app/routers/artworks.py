from fastapi import APIRouter, Query

from app.services.art_institute import search_artworks

router = APIRouter(prefix="/artworks", tags=["Artworks"])


@router.get("/search")
async def search(
    q: str = Query(default="", description="Search term"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    return await search_artworks(query=q, page=page, limit=limit)
