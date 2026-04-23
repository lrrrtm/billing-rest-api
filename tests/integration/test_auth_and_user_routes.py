from __future__ import annotations

from httpx import AsyncClient


async def test_user_can_login_and_get_profile(client: AsyncClient) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "user12345"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = await client.get("/api/v1/me", headers=headers)

    assert me_response.status_code == 200
    assert me_response.json() == {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
    }


async def test_user_can_get_accounts_and_payments(
    client: AsyncClient,
    user_token: str,
) -> None:
    headers = {"Authorization": f"Bearer {user_token}"}

    accounts_response = await client.get("/api/v1/accounts", headers=headers)
    payments_response = await client.get("/api/v1/payments", headers=headers)

    assert accounts_response.status_code == 200
    assert accounts_response.json() == [{"id": 1, "balance": "0.00"}]
    assert payments_response.status_code == 200
    assert payments_response.json() == []


async def test_access_requires_valid_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/me")

    assert response.status_code == 401
