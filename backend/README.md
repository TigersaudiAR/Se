# TwoCards Backend

FastAPI + SQLModel backend providing authentication, products, and order management for the TwoCards demo storefront.

## Quick start

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

The API is then available at [http://127.0.0.1:8001](http://127.0.0.1:8001) with Swagger documentation under `/docs`.

## Default configuration

- SQLite database stored in `twocards.db` by default.
- Override with `DATABASE_URL` (e.g. PostgreSQL) if required.
- JWT settings configurable with `JWT_SECRET`, `JWT_ALGO`, and `ACCESS_TOKEN_EXPIRE_MINUTES` environment variables.

## First run checklist

1. Register a user via `POST /auth/register`.
2. Promote the user to admin by updating the database manually (or extend the API) so they can create products.
3. Authenticate via `POST /auth/login` to retrieve an access token.
4. Use the token (Bearer) to call `POST /products` and populate catalog items.

