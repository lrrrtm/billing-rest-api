from __future__ import annotations

from decimal import Decimal

from app.core.security import (
    build_webhook_signature,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    verify_webhook_signature,
)


def test_hash_password_and_verify_password() -> None:
    password = "user12345"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_access_token_creation_and_decoding() -> None:
    token = create_access_token(user_id=15, role="admin")

    payload = decode_access_token(token)

    assert payload["sub"] == "15"
    assert payload["role"] == "admin"


def test_webhook_signature_matches_expected_example() -> None:
    signature = build_webhook_signature(
        account_id=1,
        amount=Decimal("100"),
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=1,
        secret_key="gfdmhghif38yrf9ew0jkf32",
    )

    assert signature == "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
    assert verify_webhook_signature(
        account_id=1,
        amount=Decimal("100"),
        transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=1,
        signature=signature,
        secret_key="gfdmhghif38yrf9ew0jkf32",
    )
