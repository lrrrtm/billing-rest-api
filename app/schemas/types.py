from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import Field

MoneyDecimal = Annotated[
    Decimal,
    Field(
        ge=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        description="Денежная сумма в формате с двумя знаками после запятой.",
        json_schema_extra={"example": "100.00"},
    ),
]

PositiveMoneyDecimal = Annotated[
    Decimal,
    Field(
        gt=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        description="Положительная денежная сумма в формате с двумя знаками после запятой.",
        json_schema_extra={"example": "100.00"},
    ),
]
