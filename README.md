# Travel Planner API

A REST API for managing travel projects and places, built with FastAPI, SQLModel, and PostgreSQL.

Travellers can create projects, add places from the [Art Institute of Chicago API](https://api.artic.edu/docs/), attach notes, and mark places as visited. When all places in a project are visited, the project is automatically marked as completed.

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

### Option B — Local

**Requirements:** Python 3.12+, PostgreSQL running locally

```bash
cp .env.example .env
# In .env, uncomment the localhost line and remove the Docker line

pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

API: http://localhost:8000

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string (see `.env.example`) | — |
| `API_USERNAME` | Basic Auth username | `admin` |
| `API_PASSWORD` | Basic Auth password | `secret` |

## Authentication

All endpoints require **HTTP Basic Auth**. Set credentials via `API_USERNAME` and `API_PASSWORD` in `.env`.

In Postman: **Authorization tab → Basic Auth → enter username and password.**

In curl:
```bash
curl -u admin:secret http://localhost:8000/projects/
```

## API Endpoints

### Projects

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/projects/` | Create a project (optionally with places) |
| `GET` | `/projects/` | List all projects (supports `offset` & `limit`) |
| `GET` | `/projects/{id}` | Get a project with its places |
| `PATCH` | `/projects/{id}` | Update project name, description, or start date |
| `DELETE` | `/projects/{id}` | Delete a project (blocked if any place is visited) |

### Places

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/projects/{id}/places` | Add a place to a project (validated against Art Institute API) |
| `GET` | `/projects/{id}/places` | List all places in a project |
| `GET` | `/projects/{id}/places/{place_id}` | Get a single place |
| `PATCH` | `/projects/{id}/places/{place_id}` | Update notes or mark as visited |

## Business Rules

- A project can have **1–10 places**
- The same place cannot be added to a project more than once
- A project **cannot be deleted** if any of its places are marked as visited
- When **all places are visited**, the project is automatically marked as completed
- Places are validated against the [Art Institute of Chicago API](https://api.artic.edu/docs/) before being stored

## API Documentation

**Swagger UI** — interactive docs available at [`/docs`](http://localhost:8000/docs) when the app is running.

**Postman Collection** — import `postman_collection.json` from this repository:
1. Open Postman → **Import**
2. Select the file `postman_collection.json`
3. Set the `base_url` variable to `http://localhost:8000`

Alternatively, import directly from the running app:
**Import → Link** → `http://localhost:8000/openapi.json`

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```
