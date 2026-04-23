from __future__ import annotations

from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import build_webhook_signature
from app.models import Account, User, UserRole


def _build_payload(
    *,
    transaction_id: str,
    account_id: int,
    user_id: int,
    amount: str,
) -> dict[str, object]:
    signature = build_webhook_signature(
        account_id=account_id,
        amount=Decimal(amount),
        transaction_id=transaction_id,
        user_id=user_id,
        secret_key="gfdmhghif38yrf9ew0jkf32",
    )
    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "user_id": user_id,
        "amount": amount,
        "signature": signature,
    }


async def test_webhook_creates_missing_account_and_adds_balance(
    client: AsyncClient,
    user_token: str,
) -> None:
    payload = _build_payload(
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        account_id=99,
        user_id=1,
        amount="100.00",
    )

    response = await client.post("/api/v1/webhooks/payments", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["account_id"] == 99
    assert response.json()["balance"] == "100.00"

    accounts_response = await client.get(
        "/api/v1/accounts",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert accounts_response.status_code == 200
    assert accounts_response.json() == [
        {"id": 1, "balance": "0.00"},
        {"id": 99, "balance": "100.00"},
    ]


async def test_duplicate_webhook_does_not_change_balance(client: AsyncClient) -> None:
    payload = _build_payload(
        transaction_id="95dcc8d5-21e6-44d0-bf09-a4a3b935b9a4",
        account_id=1,
        user_id=1,
        amount="42.50",
    )

    first_response = await client.post("/api/v1/webhooks/payments", json=payload)
    second_response = await client.post("/api/v1/webhooks/payments", json=payload)

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "processed"
    assert first_response.json()["balance"] == "42.50"

    assert second_response.status_code == 200
    assert second_response.json()["status"] == "duplicate_ignored"
    assert second_response.json()["balance"] == "42.50"


async def test_webhook_returns_409_when_account_belongs_to_another_user(
    client: AsyncClient,
    db_session,
) -> None:
    another_user = User(
        email="second-user@example.com",
        full_name="Second User",
        password_hash="not-used",
        role=UserRole.USER,
    )
    db_session.add(another_user)
    await db_session.flush()

    account = Account(id=77, user_id=another_user.id, balance=Decimal("0.00"))
    db_session.add(account)
    await db_session.commit()

    payload = _build_payload(
        transaction_id="525cf775-90a3-4789-9432-49fd215d9f85",
        account_id=77,
        user_id=1,
        amount="50.00",
    )

    response = await client.post("/api/v1/webhooks/payments", json=payload)

    assert response.status_code == 409


async def test_webhook_returns_404_for_unknown_user(client: AsyncClient) -> None:
    payload = _build_payload(
        transaction_id="28b2bc04-0f94-4764-b405-63aa0eb5ed0d",
        account_id=55,
        user_id=999,
        amount="10.00",
    )

    response = await client.post("/api/v1/webhooks/payments", json=payload)

    assert response.status_code == 404


async def test_webhook_rejects_invalid_signature(client: AsyncClient) -> None:
    payload = _build_payload(
        transaction_id="06347364-cb0d-4345-a1ee-a36f42b1ec89",
        account_id=1,
        user_id=1,
        amount="10.00",
    )
    payload["signature"] = "0" * 64

    response = await client.post("/api/v1/webhooks/payments", json=payload)

    assert response.status_code == 403
