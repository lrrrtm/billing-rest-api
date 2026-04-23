from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        description="Email пользователя или администратора.",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль учетной записи.",
        examples=["user12345"],
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT access token для передачи в заголовке Authorization.",
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена авторизации.",
        examples=["bearer"],
    )
