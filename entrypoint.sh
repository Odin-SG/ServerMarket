#!/usr/bin/env bash
set -euo pipefail

until psql "$DATABASE_URL" -c '\q' 2>/dev/null; do
  echo "⏳ Waiting for Postgres..."
  sleep 2
done

exec "$@"
