from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

logging.basicConfig(level=settings.log_level)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Billing REST API"
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get(
        "/health",
        tags=["health"],
        summary="Проверка состояния сервиса",
        description="Возвращает статус доступности приложения без авторизации.",
    )
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
