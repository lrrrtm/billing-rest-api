from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hasher = PasswordHash.recommended()
MONEY_PRECISION = Decimal("0.01")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(*, user_id: int, role: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )


def decimal_to_string(value: Decimal) -> str:
    normalized = value.normalize()
    return format(normalized, "f")


def build_webhook_signature(
    *,
    account_id: int,
    amount: Decimal,
    transaction_id: UUID | str,
    user_id: int,
    secret_key: str,
) -> str:
    payload = (
        f"{account_id}"
        f"{decimal_to_string(amount)}"
        f"{transaction_id}"
        f"{user_id}"
        f"{secret_key}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_webhook_signature(
    *,
    account_id: int,
    amount: Decimal,
    transaction_id: UUID | str,
    user_id: int,
    signature: str,
    secret_key: str,
) -> bool:
    expected_signature = build_webhook_signature(
        account_id=account_id,
        amount=amount,
        transaction_id=transaction_id,
        user_id=user_id,
        secret_key=secret_key,
    )
    return hmac.compare_digest(signature, expected_signature)


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_PRECISION)


__all__ = [
    "InvalidTokenError",
    "build_webhook_signature",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "quantize_money",
    "verify_password",
    "verify_webhook_signature",
]
