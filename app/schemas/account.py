from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import MoneyDecimal


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор счета.", examples=[1])
    balance: MoneyDecimal
