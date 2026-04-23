from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import SessionDep
from app.core.config import settings
from app.core.security import verify_webhook_signature
from app.schemas.webhook import PaymentWebhookRequest, PaymentWebhookResponse
from app.services.payments import AccountOwnershipConflictError, UserNotFoundError, process_payment_webhook

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments")


@router.post(
    "",
    response_model=PaymentWebhookResponse,
    summary="Обработать webhook пополнения счета",
    description=(
        "Проверяет подпись webhook payload, при необходимости создает счет пользователю, "
        "сохраняет платеж и пополняет баланс. Повторный transaction_id обрабатывается идемпотентно."
    ),
    responses={
        403: {"description": "Некорректная подпись webhook."},
        404: {"description": "Пользователь не найден."},
        409: {"description": "Счет принадлежит другому пользователю."},
    },
)
async def handle_payment_webhook(
    payload: PaymentWebhookRequest,
    session: SessionDep,
) -> PaymentWebhookResponse:
    if not verify_webhook_signature(
        account_id=payload.account_id,
        amount=payload.amount,
        transaction_id=payload.transaction_id,
        user_id=payload.user_id,
        signature=payload.signature,
        secret_key=settings.webhook_secret,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )

    try:
        result = await process_payment_webhook(session=session, payload=payload)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc
    except AccountOwnershipConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account belongs to another user",
        ) from exc

    logger.info(
        "Webhook processed: transaction_id=%s status=%s account_id=%s",
        payload.transaction_id,
        result.status,
        result.account_id,
    )
    return PaymentWebhookResponse(
        status=result.status,
        transaction_id=payload.transaction_id,
        account_id=result.account_id,
        balance=result.balance,
    )
