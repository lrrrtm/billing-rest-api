from __future__ import annotations

import pytest_asyncio
from sqlalchemy import text


@pytest_asyncio.fixture(autouse=True)
async def reset_database_state(configure_environment: None) -> None:
    from app.db.session import engine

    async with engine.begin() as connection:
        await connection.execute(text("DELETE FROM payments"))
        await connection.execute(text("DELETE FROM accounts"))
        await connection.execute(text("DELETE FROM users WHERE id NOT IN (1, 2)"))
        await connection.execute(
            text(
                """
                INSERT INTO accounts (id, user_id, balance)
                VALUES (1, 1, 0)
                ON CONFLICT (id) DO UPDATE
                SET user_id = EXCLUDED.user_id, balance = EXCLUDED.balance
                """
            )
        )
        await connection.execute(
            text(
                """
                UPDATE users
                SET email = 'user@example.com', full_name = 'Test User', role = 'user'
                WHERE id = 1
                """
            )
        )
        await connection.execute(
            text(
                """
                UPDATE users
                SET email = 'admin@example.com', full_name = 'Test Admin', role = 'admin'
                WHERE id = 2
                """
            )
        )
        await connection.execute(
            text("SELECT setval(pg_get_serial_sequence('users', 'id'), 2, true)")
        )
        await connection.execute(
            text("SELECT setval(pg_get_serial_sequence('accounts', 'id'), 1, true)")
        )
        await connection.execute(
            text("SELECT setval(pg_get_serial_sequence('payments', 'id'), 1, false)")
        )

    yield
