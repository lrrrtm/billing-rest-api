from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import PositiveMoneyDecimal


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор платежа в базе данных.", examples=[1])
    transaction_id: UUID = Field(
        description="Уникальный идентификатор транзакции во внешней платежной системе.",
        examples=["5eae174f-7cd0-472c-bd36-35660f00132b"],
    )
    account_id: int = Field(description="Идентификатор счета, который был пополнен.", examples=[1])
    amount: PositiveMoneyDecimal
    created_at: datetime = Field(
        description="Дата и время создания платежа в UTC.",
        examples=["2026-04-23T12:00:00Z"],
    )
