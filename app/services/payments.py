from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import quantize_money
from app.models import Account, Payment, User
from app.schemas.webhook import PaymentWebhookRequest


class UserNotFoundError(Exception):
    """Пользователь не найден."""


class AccountOwnershipConflictError(Exception):
    """Счет привязан к другому пользователю."""


@dataclass(slots=True)
class PaymentWebhookResult:
    status: str
    account_id: int
    balance: Decimal


async def process_payment_webhook(
    *,
    session: AsyncSession,
    payload: PaymentWebhookRequest,
) -> PaymentWebhookResult:
    amount = quantize_money(payload.amount)

    async with session.begin():
        user = await session.scalar(select(User.id).where(User.id == payload.user_id))
        if user is None:
            raise UserNotFoundError

        account = await session.scalar(
            select(Account).where(Account.id == payload.account_id).with_for_update()
        )
        if account is not None and account.user_id != payload.user_id:
            raise AccountOwnershipConflictError

        if account is None:
            await session.execute(
                insert(Account)
                .values(id=payload.account_id, user_id=payload.user_id, balance=0)
                .on_conflict_do_nothing(index_elements=[Account.id])
            )
            account = await session.scalar(
                select(Account).where(Account.id == payload.account_id).with_for_update()
            )
            if account is None:
                raise RuntimeError("Account creation failed")
            if account.user_id != payload.user_id:
                raise AccountOwnershipConflictError

        insert_payment = await session.execute(
            insert(Payment)
            .values(
                transaction_id=payload.transaction_id,
                user_id=payload.user_id,
                account_id=payload.account_id,
                amount=amount,
            )
            .on_conflict_do_nothing(index_elements=[Payment.transaction_id])
            .returning(Payment.id)
        )
        payment_id = insert_payment.scalar_one_or_none()
        if payment_id is None:
            return PaymentWebhookResult(
                status="duplicate_ignored",
                account_id=account.id,
                balance=account.balance,
            )

        await session.execute(
            update(Account)
            .where(Account.id == account.id)
            .values(balance=Account.balance + amount)
        )
        await session.refresh(account)
        return PaymentWebhookResult(
            status="processed",
            account_id=account.id,
            balance=account.balance,
        )
