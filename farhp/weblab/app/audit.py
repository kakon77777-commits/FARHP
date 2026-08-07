from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import AuditEvent, AuditHead


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_hex(value) -> str:
    if not isinstance(value, str):
        value = canonical_json(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def append_event(db: Session, entity_type: str, entity_id: str, event_type: str, payload: dict) -> AuditEvent:
    head = db.scalar(
        select(AuditHead)
        .where(AuditHead.entity_type == entity_type, AuditHead.entity_id == entity_id)
        .with_for_update()
    )
    if head is None:
        head = AuditHead(entity_type=entity_type, entity_id=entity_id, next_index=0, head_hash="0" * 64)
        db.add(head)
        db.flush()
    index = head.next_index
    prev = head.head_hash
    body = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "event_index": index,
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev,
    }
    digest = sha256_hex(body)
    event = AuditEvent(
        entity_type=entity_type,
        entity_id=entity_id,
        event_index=index,
        event_type=event_type,
        payload_json=canonical_json(payload),
        prev_hash=prev,
        event_hash=digest,
    )
    db.add(event)
    head.next_index = index + 1
    head.head_hash = digest
    head.updated_at = datetime.now(timezone.utc)
    db.flush()
    return event


def events_for(db: Session, entity_type: str, entity_id: str) -> list[AuditEvent]:
    return list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
            .order_by(AuditEvent.event_index)
        )
    )


def verify_events(events: list[AuditEvent]) -> dict:
    prev = "0" * 64
    for expected, event in enumerate(events):
        payload = json.loads(event.payload_json)
        body = {
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "event_index": event.event_index,
            "event_type": event.event_type,
            "payload": payload,
            "prev_hash": prev,
        }
        computed = sha256_hex(body)
        if event.event_index != expected or event.prev_hash != prev or event.event_hash != computed:
            return {"valid": False, "failed_index": expected, "event_count": len(events), "head": events[-1].event_hash if events else None}
        prev = event.event_hash
    return {"valid": True, "failed_index": None, "event_count": len(events), "head": prev if events else None}
