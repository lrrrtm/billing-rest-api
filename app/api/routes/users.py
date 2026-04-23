from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import SessionDep, get_current_user
from app.models import Account, Payment, User
from app.schemas.account import AccountResponse
from app.schemas.payment import PaymentResponse
from app.schemas.user import UserResponse

router = APIRouter()
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить данные текущего пользователя",
    description="Возвращает id, email и полное имя авторизованного пользователя.",
    responses={401: {"description": "Требуется валидный Bearer token."}},
)
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get(
    "/accounts",
    response_model=list[AccountResponse],
    summary="Получить список своих счетов",
    description="Возвращает все счета текущего пользователя и их балансы.",
    responses={401: {"description": "Требуется валидный Bearer token."}},
)
async def get_accounts(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[AccountResponse]:
    result = await session.scalars(
        select(Account)
        .where(Account.user_id == current_user.id)
        .order_by(Account.id)
    )
    return [AccountResponse.model_validate(account) for account in result.all()]


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
    summary="Получить список своих платежей",
    description="Возвращает все платежи текущего пользователя в обратном хронологическом порядке.",
    responses={401: {"description": "Требуется валидный Bearer token."}},
)
async def get_payments(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[PaymentResponse]:
    result = await session.scalars(
        select(Payment)
        .options(selectinload(Payment.account))
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc(), Payment.id.desc())
    )
    return [PaymentResponse.model_validate(payment) for payment in result.all()]
