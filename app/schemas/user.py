from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.account import AccountResponse


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор пользователя.", examples=[1])
    email: EmailStr = Field(description="Email пользователя.", examples=["user@example.com"])
    full_name: str = Field(description="Полное имя пользователя.", examples=["Test User"])


class AdminUserResponse(UserResponse):
    accounts: list[AccountResponse] = Field(
        description="Список счетов пользователя с текущими балансами.",
    )


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(
        description="Email нового пользователя.",
        examples=["new-user@example.com"],
    )
    full_name: str = Field(
        min_length=1,
        max_length=255,
        description="Полное имя нового пользователя.",
        examples=["New User"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль нового пользователя.",
        examples=["new-user-password"],
    )


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        description="Новый email пользователя.",
        examples=["updated-user@example.com"],
    )
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Новое полное имя пользователя.",
        examples=["Updated User"],
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Новый пароль пользователя.",
        examples=["updated-user-password"],
    )
