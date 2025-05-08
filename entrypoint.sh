#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-a_stor_shop}"

echo "Ждём Postgres на $DB_HOST:$DB_PORT..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
  echo "$(date +'%Y-%m-%d %H:%M:%S') ⏳ Waiting for Postgres..."
  sleep 2
done

echo "Postgres доступен — стартуем: $*"
exec "$@"
