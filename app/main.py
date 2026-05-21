import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.database import engine
from app.models import Base
from app.routers import artworks, places, projects

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    description="CRUD API for managing travel projects with artworks from the Art Institute of Chicago.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(projects.router)
app.include_router(places.router)
app.include_router(artworks.router)


@app.exception_handler(httpx.TimeoutException)
async def timeout_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": "Art Institute of Chicago API timed out"})


@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request, exc):
    return JSONResponse(
        status_code=502,
        content={"detail": f"Art Institute of Chicago API returned an error: {exc.response.status_code}"},
    )


@app.exception_handler(httpx.RequestError)
async def request_error_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": "Art Institute of Chicago API is unreachable"})


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
