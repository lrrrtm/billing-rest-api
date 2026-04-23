"""Seed default users."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pwdlib import PasswordHash

revision = "0002_seed_default_data"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    password_hasher = PasswordHash.recommended()
    user_password_hash = password_hasher.hash("user12345")
    admin_password_hash = password_hasher.hash("admin12345")

    op.execute(
        sa.text(
            """
            INSERT INTO users (id, email, full_name, password_hash, role)
            VALUES
                (1, 'user@example.com', 'Test User', :user_password_hash, 'user'),
                (2, 'admin@example.com', 'Test Admin', :admin_password_hash, 'admin')
            """
        ).bindparams(
            user_password_hash=user_password_hash,
            admin_password_hash=admin_password_hash,
        )
    )

    op.execute(
        sa.text(
            """
            INSERT INTO accounts (id, user_id, balance)
            VALUES (1, 1, 0)
            """
        )
    )

    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('users', 'id'), 2, true)"))
    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('accounts', 'id'), 1, true)"))
    op.execute(sa.text("SELECT setval(pg_get_serial_sequence('payments', 'id'), 1, false)"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM accounts WHERE id = 1"))
    op.execute(sa.text("DELETE FROM users WHERE id IN (1, 2)"))
