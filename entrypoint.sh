#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-a_stor_shop}"

echo "Ждём, пока Postgres поднимется..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
  sleep 2
done

echo "Postgres доступен — ждём генерации таблиц…"
until psql "$DATABASE_URL" -tAc "SELECT 1 FROM servers LIMIT 1" >/dev/null 2>&1; do
  echo "…schema not ready, sleeping 2s"
  sleep 2
done

echo "Схема готова — стартуем: $*"
exec "$@"
