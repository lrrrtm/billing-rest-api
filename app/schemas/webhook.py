from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.types import MoneyDecimal, PositiveMoneyDecimal


class PaymentWebhookRequest(BaseModel):
    transaction_id: UUID = Field(
        description="Уникальный идентификатор транзакции в сторонней системе.",
        examples=["5eae174f-7cd0-472c-bd36-35660f00132b"],
    )
    account_id: int = Field(
        gt=0,
        description="Идентификатор счета пользователя во внутренней системе.",
        examples=[1],
    )
    user_id: int = Field(
        gt=0,
        description="Идентификатор пользователя во внутренней системе.",
        examples=[1],
    )
    amount: PositiveMoneyDecimal
    signature: str = Field(
        min_length=64,
        max_length=64,
        description="SHA256-подпись webhook payload.",
        examples=["7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"],
    )


class PaymentWebhookResponse(BaseModel):
    status: str = Field(
        description="Результат обработки webhook: processed или duplicate_ignored.",
        examples=["processed"],
    )
    transaction_id: UUID = Field(
        description="Идентификатор обработанной транзакции.",
        examples=["5eae174f-7cd0-472c-bd36-35660f00132b"],
    )
    account_id: int = Field(description="Идентификатор счета пользователя.", examples=[1])
    balance: MoneyDecimal
