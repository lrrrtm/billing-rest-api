from __future__ import annotations

import time

import psycopg

from app.core.config import settings


def main() -> None:
    sync_url = settings.sync_database_url.replace("+psycopg", "")

    for _ in range(30):
        try:
            with psycopg.connect(sync_url):
                return
        except psycopg.OperationalError:
            time.sleep(2)

    raise RuntimeError("Database is not available")


if __name__ == "__main__":
    main()
