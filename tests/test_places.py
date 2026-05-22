import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.place import Place
from app.models.project import Project


@pytest.fixture
async def project(client: AsyncClient):
    response = await client.post("/projects/", json={"name": "My Trip"})
    return response.json()


@pytest.fixture
async def project_with_place(client: AsyncClient, mock_artwork):
    response = await client.post(
        "/projects/",
        json={"name": "Art Trip", "places": [{"external_id": 16568}]},
    )
    return response.json()


async def test_add_place(client: AsyncClient, project, mock_artwork):
    response = await client.post(
        f"/projects/{project['id']}/places",
        json={"external_id": 16568},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["external_id"] == 16568
    assert data["title"] == "Water Lilies"
    assert data["visited"] is False
    assert data["notes"] is None


async def test_add_place_project_not_found(client: AsyncClient, mock_artwork):
    response = await client.post("/projects/999/places", json={"external_id": 16568})
    assert response.status_code == 404


async def test_add_place_artwork_not_found(
    client: AsyncClient, project, mock_artwork_not_found
):
    response = await client.post(
        f"/projects/{project['id']}/places",
        json={"external_id": 99999},
    )
    assert response.status_code == 400


async def test_add_place_duplicate(client: AsyncClient, project_with_place, mock_artwork):
    project_id = project_with_place["id"]
    response = await client.post(
        f"/projects/{project_id}/places",
        json={"external_id": 16568},
    )
    assert response.status_code == 400


async def test_add_place_max_limit(
    client: AsyncClient, session: AsyncSession, mock_artwork
):
    create = await client.post("/projects/", json={"name": "Full Trip"})
    project_id = create.json()["id"]

    for i in range(10):
        session.add(Place(project_id=project_id, external_id=i, title=f"Place {i}"))
    await session.commit()

    response = await client.post(
        f"/projects/{project_id}/places",
        json={"external_id": 999},
    )
    assert response.status_code == 400


async def test_list_places(client: AsyncClient, project_with_place):
    project_id = project_with_place["id"]
    response = await client.get(f"/projects/{project_id}/places")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_place(client: AsyncClient, project_with_place):
    project_id = project_with_place["id"]
    place_id = project_with_place["places"][0]["id"]
    response = await client.get(f"/projects/{project_id}/places/{place_id}")
    assert response.status_code == 200
    assert response.json()["id"] == place_id


async def test_get_place_not_found(client: AsyncClient, project):
    response = await client.get(f"/projects/{project['id']}/places/999")
    assert response.status_code == 404


async def test_update_place_notes(client: AsyncClient, project_with_place):
    project_id = project_with_place["id"]
    place_id = project_with_place["places"][0]["id"]
    response = await client.patch(
        f"/projects/{project_id}/places/{place_id}",
        json={"notes": "Must see!"},
    )
    assert response.status_code == 200
    assert response.json()["notes"] == "Must see!"
    assert response.json()["visited"] is False


async def test_mark_place_visited(client: AsyncClient, project_with_place):
    project_id = project_with_place["id"]
    place_id = project_with_place["places"][0]["id"]
    response = await client.patch(
        f"/projects/{project_id}/places/{place_id}",
        json={"visited": True},
    )
    assert response.status_code == 200
    assert response.json()["visited"] is True


async def test_project_auto_completes_when_all_visited(
    client: AsyncClient, session: AsyncSession, mock_artwork
):
    create = await client.post(
        "/projects/",
        json={"name": "Short Trip", "places": [{"external_id": 16568}]},
    )
    project_id = create.json()["id"]
    place_id = create.json()["places"][0]["id"]

    await client.patch(
        f"/projects/{project_id}/places/{place_id}",
        json={"visited": True},
    )

    result = await session.exec(select(Project).where(Project.id == project_id))
    project = result.first()
    assert project.is_completed is True


async def test_project_not_completed_when_some_unvisited(
    client: AsyncClient, session: AsyncSession, mock_artwork
):
    create = await client.post(
        "/projects/",
        json={
            "name": "Long Trip",
            "places": [{"external_id": 16568}],
        },
    )
    project_id = create.json()["id"]

    session.add(Place(project_id=project_id, external_id=999, title="Other Place"))
    await session.commit()

    place_id = create.json()["places"][0]["id"]
    await client.patch(
        f"/projects/{project_id}/places/{place_id}",
        json={"visited": True},
    )

    result = await session.exec(select(Project).where(Project.id == project_id))
    project = result.first()
    assert project.is_completed is False
