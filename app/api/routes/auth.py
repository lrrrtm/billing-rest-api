from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import SessionDep
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Авторизация пользователя или администратора",
    description=(
        "Проверяет email и пароль, затем возвращает JWT access token "
        "для доступа к защищенным маршрутам."
    ),
    responses={
        401: {"description": "Неверный email или пароль."},
    },
)
async def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=create_access_token(user_id=user.id, role=user.role.value),
    )
