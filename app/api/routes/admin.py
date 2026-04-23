from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.api.dependencies import SessionDep, get_admin_user
from app.core.security import hash_password
from app.models import User, UserRole
from app.schemas.user import (
    AdminUserResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/users")
AdminDep = Annotated[User, Depends(get_admin_user)]


async def _get_regular_user_or_404(session: SessionDep, user_id: int) -> User:
    user = await session.scalar(
        select(User)
        .options(selectinload(User.accounts))
        .where(User.id == user_id, User.role == UserRole.USER)
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get(
    "",
    response_model=list[AdminUserResponse],
    summary="Получить список пользователей",
    description="Возвращает список обычных пользователей вместе с их счетами и балансами.",
    responses={
        401: {"description": "Требуется валидный Bearer token."},
        403: {"description": "Маршрут доступен только администратору."},
    },
)
async def list_users(
    session: SessionDep,
    _: AdminDep,
) -> list[AdminUserResponse]:
    users = await session.scalars(
        select(User)
        .options(selectinload(User.accounts))
        .where(User.role == UserRole.USER)
        .order_by(User.id)
    )
    return [AdminUserResponse.model_validate(user) for user in users.all()]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создает нового пользователя.",
    responses={
        401: {"description": "Требуется валидный Bearer token."},
        403: {"description": "Маршрут доступен только администратору."},
        409: {"description": "Пользователь с таким email уже существует."},
    },
)
async def create_user(
    payload: UserCreateRequest,
    session: SessionDep,
    _: AdminDep,
) -> UserResponse:
    existing_user = await session.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
    description="Обновляет email, имя и/или пароль существующего обычного пользователя.",
    responses={
        401: {"description": "Требуется валидный Bearer token."},
        403: {"description": "Маршрут доступен только администратору."},
        404: {"description": "Пользователь не найден."},
        409: {"description": "Конфликт данных пользователя, например duplicate email."},
    },
)
async def update_user(
    user_id: Annotated[
        int,
        Path(description="Идентификатор пользователя для обновления.", examples=[1]),
    ],
    payload: UserUpdateRequest,
    session: SessionDep,
    _: AdminDep,
) -> UserResponse:
    user = await _get_regular_user_or_404(session, user_id)

    if payload.email is not None and payload.email != user.email:
        existing_user = await session.scalar(select(User).where(User.email == payload.email))
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )
        user.email = payload.email

    if payload.full_name is not None:
        user.full_name = payload.full_name

    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User update conflict",
        ) from exc

    await session.refresh(user)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удаляет обычного пользователя и все связанные с ним счета и платежи.",
    responses={
        401: {"description": "Требуется валидный Bearer token."},
        403: {"description": "Маршрут доступен только администратору."},
        404: {"description": "Пользователь не найден."},
    },
)
async def delete_user(
    user_id: Annotated[
        int,
        Path(description="Идентификатор пользователя для удаления.", examples=[1]),
    ],
    session: SessionDep,
    _: AdminDep,
) -> Response:
    user = await _get_regular_user_or_404(session, user_id)
    await session.delete(user)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
