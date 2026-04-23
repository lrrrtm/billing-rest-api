# Billing REST API

Асинхронное REST API на `FastAPI` для пользователей, администраторов, счетов и платежей.

## Запуск через Docker Compose

1. Создать `.env` на основе `.env.example`.
2. Выполнить:

```bash
docker compose up --build
```

3. API будет доступно на `http://localhost:8000`.

## Локальный запуск без Docker

1. Установить `uv`, если он еще не установлен:

```bash
python -m pip install uv
```

2. Создать `.env` на основе `.env.example`.
3. Установить зависимости:

```bash
uv sync
```

4. Поднять PostgreSQL и применить миграции:

```bash
uv run alembic upgrade head
```

5. Запустить приложение:

```bash
uv run uvicorn app.main:app --reload
```

## Дефолтные учетные записи

- Пользователь: `user@example.com` / `user12345`
- Администратор: `admin@example.com` / `admin12345`

## Основные маршруты

- `POST /api/v1/auth/login`
- `GET /api/v1/me`
- `GET /api/v1/accounts`
- `GET /api/v1/payments`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{user_id}`
- `DELETE /api/v1/admin/users/{user_id}`
- `POST /api/v1/webhooks/payments`
