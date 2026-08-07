# FARHP v1.0 RC Data Model

## Core tables

```text
users
research_plans
preregistration_archives
invites
study_sessions
audit_events
audit_heads
alembic_version
```

## Authentication

`users` supports two account origins:

- `auth_provider = local` with Argon2 `password_hash`;
- `auth_provider = oidc:<issuer>` with `external_subject`.

`(auth_provider, external_subject)` is unique. `token_version` allows server-side revocation of previously issued signed tokens.

## Audit head

`audit_heads` stores one mutable chain head per entity:

```text
(entity_type, entity_id) → (next_index, head_hash)
```

Each append locks the head row, writes the event and advances the head in the same transaction. PostgreSQL supplies row-level locking; SQLite serializes write transactions and is retained for single-node use.

## Payload compatibility

The relational shell is v1.0 RC, while the embedded research payloads remain compatible with v0.8:

- Research plan v0.8
- Checkpoint v0.8
- Multi-stimulus study v0.8

This prevents the productionization layer from silently changing the experiment semantics.
