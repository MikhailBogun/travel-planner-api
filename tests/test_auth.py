from httpx import AsyncClient


async def test_no_credentials_returns_401(raw_client: AsyncClient):
    response = await raw_client.get("/projects/")
    assert response.status_code == 401


async def test_wrong_password_returns_401(raw_client: AsyncClient):
    response = await raw_client.get("/projects/", auth=("admin", "wrongpassword"))
    assert response.status_code == 401


async def test_wrong_username_returns_401(raw_client: AsyncClient):
    response = await raw_client.get("/projects/", auth=("hacker", "secret"))
    assert response.status_code == 401


async def test_correct_credentials_returns_200(raw_client: AsyncClient):
    response = await raw_client.get("/projects/", auth=("admin", "secret"))
    assert response.status_code == 200
