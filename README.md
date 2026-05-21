# Travel Planner API

FastAPI + SQLite. Manage trips and places (artworks from the Art Institute of Chicago API).

## Run

```bash
docker compose up --build
```

Or:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API on `http://localhost:8000`. Swagger UI on `/docs`.

## Postman

Import `travel_planner.postman_collection.json`, set `base_url` to `http://localhost:8000`.

## Config

```
DATABASE_URL=sqlite:///./travel_planner.db
```
