# Travel Planner API

A REST API for managing travel projects and places, built with FastAPI, SQLModel, and PostgreSQL.

Travellers can create projects, add places from the [Art Institute of Chicago API](https://api.artic.edu/docs/), attach notes, and mark places as visited.

## Tech Stack

- **FastAPI** — async REST API
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **PostgreSQL** — relational database
- **Alembic** — database migrations
- **Docker / Docker Compose** — containerized local setup

## Getting Started

### Option A — Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  
OpenAPI JSON (Postman import): http://localhost:8000/openapi.json

### Option B — Local

**Requirements:** Python 3.12+, PostgreSQL running locally

```bash
cp .env.example .env
# In .env, uncomment the localhost line and remove the Docker line

pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string (see `.env.example`) |

## API Documentation

Interactive Swagger UI is available at `/docs` when the app is running.

To import into Postman: **Import → Link** → `http://localhost:8000/openapi.json`
