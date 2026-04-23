from __future__ import annotations

from httpx import AsyncClient


async def test_admin_can_list_regular_users(
    client: AsyncClient,
    admin_token: str,
) -> None:
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "email": "user@example.com",
            "full_name": "Test User",
            "accounts": [{"id": 1, "balance": "0.00"}],
        }
    ]


async def test_admin_can_create_update_and_delete_user(
    client: AsyncClient,
    admin_token: str,
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}

    create_response = await client.post(
        "/api/v1/admin/users",
        headers=headers,
        json={
            "email": "new-user@example.com",
            "full_name": "New User",
            "password": "new-user-password",
        },
    )
    assert create_response.status_code == 201
    created_user = create_response.json()

    update_response = await client.patch(
        f"/api/v1/admin/users/{created_user['id']}",
        headers=headers,
        json={
            "full_name": "Updated User",
            "password": "updated-user-password",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated User"

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "new-user@example.com",
            "password": "updated-user-password",
        },
    )
    assert login_response.status_code == 200
    user_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    accounts_response = await client.get("/api/v1/accounts", headers=user_headers)
    assert accounts_response.status_code == 200
    assert accounts_response.json() == []

    delete_response = await client.delete(
        f"/api/v1/admin/users/{created_user['id']}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    users_response = await client.get("/api/v1/admin/users", headers=headers)
    user_ids = [user["id"] for user in users_response.json()]
    assert created_user["id"] not in user_ids


async def test_regular_user_cannot_access_admin_endpoints(
    client: AsyncClient,
    user_token: str,
) -> None:
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403
