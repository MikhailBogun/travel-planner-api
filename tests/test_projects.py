import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.place import Place


async def test_create_project(client: AsyncClient):
    response = await client.post("/projects/", json={"name": "Italy Trip"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Italy Trip"
    assert data["is_completed"] is False
    assert data["places"] == []


async def test_create_project_with_places(client: AsyncClient, mock_artwork):
    response = await client.post(
        "/projects/",
        json={"name": "Art Tour", "places": [{"external_id": 16568}]},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["places"]) == 1
    assert data["places"][0]["title"] == "Water Lilies"
    assert data["places"][0]["visited"] is False


async def test_create_project_artwork_not_found(client: AsyncClient, mock_artwork_not_found):
    response = await client.post(
        "/projects/",
        json={"name": "Art Tour", "places": [{"external_id": 99999}]},
    )
    assert response.status_code == 400


async def test_create_project_too_many_places(client: AsyncClient):
    places = [{"external_id": i} for i in range(11)]
    response = await client.post("/projects/", json={"name": "Big Trip", "places": places})
    assert response.status_code == 422


async def test_create_project_duplicate_places(client: AsyncClient):
    response = await client.post(
        "/projects/",
        json={"name": "Trip", "places": [{"external_id": 1}, {"external_id": 1}]},
    )
    assert response.status_code == 422


async def test_list_projects(client: AsyncClient):
    await client.post("/projects/", json={"name": "Trip 1"})
    await client.post("/projects/", json={"name": "Trip 2"})
    response = await client.get("/projects/")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_get_project(client: AsyncClient):
    create = await client.post("/projects/", json={"name": "My Trip"})
    project_id = create.json()["id"]
    response = await client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "My Trip"


async def test_get_project_not_found(client: AsyncClient):
    response = await client.get("/projects/999")
    assert response.status_code == 404


async def test_update_project(client: AsyncClient):
    create = await client.post("/projects/", json={"name": "Old Name"})
    project_id = create.json()["id"]
    response = await client.patch(f"/projects/{project_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


async def test_delete_project(client: AsyncClient):
    create = await client.post("/projects/", json={"name": "To Delete"})
    project_id = create.json()["id"]
    response = await client.delete(f"/projects/{project_id}")
    assert response.status_code == 204


async def test_delete_project_blocked_when_visited(
    client: AsyncClient, session: AsyncSession, mock_artwork
):
    create = await client.post(
        "/projects/",
        json={"name": "Trip", "places": [{"external_id": 16568}]},
    )
    project_id = create.json()["id"]
    place_id = create.json()["places"][0]["id"]

    result = await session.exec(select(Place).where(Place.id == place_id))
    place = result.first()
    place.visited = True
    session.add(place)
    await session.commit()

    response = await client.delete(f"/projects/{project_id}")
    assert response.status_code == 400
