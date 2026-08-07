#!/usr/bin/env sh
set -eu
python scripts/migrate.py
exec uvicorn app.main:app \
  --host "${FARHP_HOST:-0.0.0.0}" \
  --port "${FARHP_PORT:-8000}" \
  --workers "${FARHP_WORKERS:-1}" \
  --proxy-headers \
  --forwarded-allow-ips "${FARHP_FORWARDED_ALLOW_IPS:-127.0.0.1}"
