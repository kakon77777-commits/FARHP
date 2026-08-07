# FARHP v1.0 RC API Reference

## Health

- `GET /api/health/live` — process liveness; does not require DB.
- `GET /api/health/ready` — DB ping plus Alembic head check; returns 503 when not ready.
- `GET /api/health` — compatibility alias for readiness.

## Authentication

- `GET /api/auth/config`
- `POST /api/auth/login`
- `GET /api/auth/oidc/login?return_to=/`
- `GET /api/auth/oidc/callback?code=...&state=...`
- `GET /api/me`

Staff endpoints use `Authorization: Bearer <token>`.

## Plans

- `POST /api/plans`
- `GET /api/plans`
- `GET /api/plans/{plan_id}`
- `POST /api/plans/{plan_id}/lock`
- `POST /api/plans/{plan_id}/archive`
- `GET /api/plans/{plan_id}/archive`
- `POST /api/plans/{plan_id}/invites`
- `GET /api/plans/{plan_id}/audit`

## Participant flow

- `GET /api/invites/{code}/public`
- `POST /api/invites/{code}/sessions`
- `GET /api/participant/sessions/{session_id}`
- `PUT /api/participant/sessions/{session_id}/checkpoint`
- `POST /api/participant/sessions/{session_id}/complete`

Participant endpoints use `X-Session-Token`.

## Staff sessions and analysis

- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `GET /api/sessions/{session_id}/audit`
- `GET /api/analysis/summary`

## Roles

| Endpoint group | PI | Collector | Analyst |
|---|---:|---:|---:|
| Plan import／lock／archive | ✓ | — | — |
| Invite creation | ✓ | ✓ | — |
| Raw session operations | ✓ | ✓ | — |
| Deidentified session view | ✓ | — | ✓ |
| Analysis | ✓ | — | ✓ |
