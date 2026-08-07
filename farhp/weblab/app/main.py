from __future__ import annotations
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
import hashlib, json, math, secrets
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session
from jsonschema import Draft202012Validator

from .config import ROOT, settings
from .db import get_db, SessionLocal, database_backend, database_ping
from .models import User, ResearchPlan, PreregistrationArchive, Invite, StudySession
from .schemas import LoginRequest, PlanImportRequest, InviteCreateRequest, ConsentRequest, CheckpointRequest, CompleteRequest
from .security import hash_password, verify_password, issue_user_token, issue_session_token, parse_session_token, current_user, require_roles
from .audit import canonical_json, sha256_hex, append_event, events_for, verify_events
from .migrations import upgrade_head, migration_status
from .middleware import SecurityHeadersMiddleware
from .oidc import authorization_url, exchange_and_validate, upsert_oidc_user

STATIC = ROOT / "static"
SCHEMA_DIR = ROOT / "spec"
PLAN_SCHEMA = json.loads((SCHEMA_DIR / "FARHP_Research_Plan_Spec_v0.8.schema.json").read_text(encoding="utf-8"))
STUDY_SCHEMA = json.loads((SCHEMA_DIR / "FARHP_MultiStimulus_Study_Spec_v0.8.schema.json").read_text(encoding="utf-8"))


def utcnow():
    return datetime.now(timezone.utc)

def parse_json(text: str | None):
    return None if text is None else json.loads(text)

def as_utc(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

def public_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "role": user.role,
        "auth_provider": user.auth_provider,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }

def plan_core(payload: dict[str, Any]) -> dict[str, Any]:
    keys = ["farhp_weblab_plan_version","study_id","task","planned_sample_size","primary_endpoint","preregistration_note","design","exclusion_policy","governance"]
    return {key: payload.get(key) for key in keys if key in payload}

def fingerprint_plan(payload: dict[str, Any]) -> dict[str, str]:
    return {"algorithm": "SHA-256", "value": sha256_hex(plan_core(payload))}

def plan_resource(plan: ResearchPlan) -> dict[str, Any]:
    payload = parse_json(plan.payload_json)
    return {"id": plan.id, "study_id": plan.study_id, "revision": plan.revision, "status": plan.status, "fingerprint": {"algorithm":plan.fingerprint_algorithm,"value":plan.fingerprint_value} if plan.fingerprint_value else None, "created_at": plan.created_at.isoformat(), "locked_at": plan.locked_at.isoformat() if plan.locked_at else None, "payload": payload, "previous_plan_id": plan.previous_plan_id}

def session_resource(session: StudySession, raw: bool = False) -> dict[str, Any]:
    base = {"id": session.id, "session_id": session.session_id, "plan_id": session.plan_id, "participant_code": session.participant_code if raw else pseudonym(session.participant_code, "PID"), "status": session.status, "created_at": session.created_at.isoformat(), "updated_at": session.updated_at.isoformat(), "completed_at": session.completed_at.isoformat() if session.completed_at else None}
    if raw:
        base.update({"consent": parse_json(session.consent_json), "checkpoint": parse_json(session.checkpoint_json), "study": parse_json(session.study_json)})
    return base

def pseudonym(value: str, prefix: str = "PID") -> str:
    digest = hashlib.sha256(f"{settings.deidentification_salt}|{value}".encode()).hexdigest()[:20]
    return f"{prefix}-{digest}"

def validate_schema(schema: dict, instance: dict, label: str):
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        path = ".".join(str(p) for p in first.path) or "$"
        raise HTTPException(status_code=422, detail=f"{label} schema error at {path}: {first.message}")

def get_participant_session(session_id: str, x_session_token: str | None, db: Session) -> StudySession:
    if not x_session_token or parse_session_token(x_session_token) != session_id:
        raise HTTPException(status_code=401, detail="participant session token required")
    session = db.scalar(select(StudySession).where(StudySession.session_id == session_id))
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session

def wilson(success: int, total: int, z: float = 1.959963984540054):
    if total <= 0: return [None, None]
    p = success / total
    denom = 1 + z*z/total
    center = (p + z*z/(2*total))/denom
    half = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/denom
    return [max(0, center-half), min(1, center+half)]

def exact_binomial_two_sided(success: int, total: int, p0: float = .5):
    if total <= 0: return None
    probs = [math.comb(total,k)*(p0**k)*((1-p0)**(total-k)) for k in range(total+1)]
    observed = probs[success]
    return min(1.0, sum(p for p in probs if p <= observed + 1e-15))

def seed_demo(db: Session):
    if not settings.demo_mode or db.scalar(select(func.count(User.id))): return
    for username, password, role in [
        ("admin", "FarhpAdmin!2026", "principal_investigator"),
        ("collector", "Collector!2026", "data_collector"),
        ("analyst", "Analyst!2026", "analyst"),
    ]:
        user = User(username=username, password_hash=hash_password(password), role=role, auth_provider="local")
        db.add(user); db.flush(); append_event(db, "user", str(user.id), "user_created", {"username": username, "role": role, "source": "demo_seed"})
    db.commit()

@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate()
    if settings.auto_migrate:
        upgrade_head()
    status = migration_status()
    if not status.get("up_to_date"):
        raise RuntimeError(f"database migration is not at head: {status}")
    with SessionLocal() as db:
        seed_demo(db)
    yield

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FARHP v1.0 RC productionization layer",
    lifespan=lifespan,
)
app.add_middleware(SecurityHeadersMiddleware, hsts_seconds=settings.hsts_seconds if settings.force_https else 0, csp_report_only=settings.csp_report_only)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(STATIC / "dashboard.html")

@app.get("/participant/{invite_code}", include_in_schema=False)
def participant_page(invite_code: str):
    return FileResponse(STATIC / "participant.html")

@app.get("/oidc-complete.html", include_in_schema=False)
def oidc_complete_page():
    return FileResponse(STATIC / "oidc-complete.html")

@app.get("/api/health/live")
def health_live():
    return {"status": "ok", "version": settings.app_version}

@app.get("/api/health/ready")
def health_ready(db: Session = Depends(get_db)):
    try:
        database_ping()
        migrations = migration_status()
        ready = bool(migrations.get("up_to_date"))
        if not ready:
            raise HTTPException(status_code=503, detail={"status": "not_ready", "migrations": migrations})
        return {"status": "ready", "version": settings.app_version, "database": database_backend(), "migrations": migrations, "users": db.scalar(select(func.count(User.id)))}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "error": str(exc)}) from exc

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return health_ready(db)

@app.get("/api/auth/config")
def auth_config():
    return {
        "local_auth_enabled": settings.local_auth_enabled,
        "oidc_enabled": settings.oidc_enabled,
        "oidc_provider_label": settings.oidc_provider_label if settings.oidc_enabled else None,
        "oidc_login_url": "/api/auth/oidc/login" if settings.oidc_enabled else None,
    }

@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    if not settings.local_auth_enabled:
        raise HTTPException(status_code=404, detail="local authentication is disabled")
    user = db.scalar(select(User).where(User.username == body.username, User.auth_provider == "local"))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    user.last_login_at = utcnow()
    append_event(db, "user", str(user.id), "login", {"username": user.username, "role": user.role, "provider": "local"})
    db.commit()
    return {"token": issue_user_token(user), "user": public_user(user)}

@app.get("/api/auth/oidc/login")
async def oidc_login(return_to: str | None = Query(default="/")):
    return RedirectResponse(await authorization_url(return_to))

@app.get("/api/auth/oidc/callback")
async def oidc_callback(code: str, state: str, db: Session = Depends(get_db)):
    claims, return_to = await exchange_and_validate(code, state)
    user = upsert_oidc_user(db, claims)
    append_event(db, "user", str(user.id), "login", {"username": user.username, "role": user.role, "provider": user.auth_provider})
    db.commit(); db.refresh(user)
    token = issue_user_token(user)
    from urllib.parse import quote
    return RedirectResponse(f"/oidc-complete.html#token={quote(token)}&return_to={quote(return_to)}")

@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return public_user(user)

@app.get("/api/users")
def users(user: User = Depends(require_roles("principal_investigator")), db: Session = Depends(get_db)):
    return [public_user(u) for u in db.scalars(select(User).order_by(User.id))]

@app.post("/api/plans")
def import_plan(body: PlanImportRequest, user: User = Depends(require_roles("principal_investigator")), db: Session = Depends(get_db)):
    source = json.loads(json.dumps(body.payload))
    if source.get("farhp_weblab_plan_version") != "0.8":
        raise HTTPException(status_code=422, detail="only FARHP WebLab plan v0.8 is supported")
    study_id = str(source.get("study_id", "")).strip()
    if not study_id: raise HTTPException(status_code=422, detail="study_id required")
    revision = (db.scalar(select(func.max(ResearchPlan.revision)).where(ResearchPlan.study_id == study_id)) or 0) + 1
    source["status"] = "draft"; source["locked_at"] = None; source["plan_fingerprint"] = None
    source.setdefault("created_at", utcnow().isoformat())
    plan = ResearchPlan(study_id=study_id, revision=revision, status="draft", payload_json=canonical_json(source), created_by_id=user.id)
    db.add(plan); db.flush()
    append_event(db, "plan", str(plan.id), "plan_imported", {"study_id": study_id, "revision": revision, "actor": user.username})
    db.commit(); db.refresh(plan)
    return plan_resource(plan)

@app.get("/api/plans")
def list_plans(user: User = Depends(require_roles("principal_investigator","data_collector","analyst")), db: Session = Depends(get_db)):
    return [plan_resource(p) for p in db.scalars(select(ResearchPlan).order_by(ResearchPlan.id.desc()))]

@app.get("/api/plans/{plan_id}")
def get_plan(plan_id: int, user: User = Depends(require_roles("principal_investigator","data_collector","analyst")), db: Session = Depends(get_db)):
    plan = db.get(ResearchPlan, plan_id)
    if not plan: raise HTTPException(404, "plan not found")
    return plan_resource(plan)

@app.post("/api/plans/{plan_id}/lock")
def lock_plan(plan_id: int, user: User = Depends(require_roles("principal_investigator")), db: Session = Depends(get_db)):
    plan = db.get(ResearchPlan, plan_id)
    if not plan: raise HTTPException(404, "plan not found")
    if plan.status != "draft": raise HTTPException(409, "plan is already immutable")
    payload = parse_json(plan.payload_json)
    fp = fingerprint_plan(payload)
    payload["status"] = "locked"; payload["locked_at"] = utcnow().isoformat(); payload["plan_fingerprint"] = fp
    validate_schema(PLAN_SCHEMA, payload, "research plan")
    plan.status = "locked"; plan.locked_at = utcnow(); plan.fingerprint_algorithm = fp["algorithm"]; plan.fingerprint_value = fp["value"]; plan.payload_json = canonical_json(payload)
    append_event(db, "plan", str(plan.id), "plan_locked", {"fingerprint": fp, "actor": user.username})
    db.commit(); db.refresh(plan)
    return plan_resource(plan)

@app.post("/api/plans/{plan_id}/archive")
def archive_plan(plan_id: int, user: User = Depends(require_roles("principal_investigator")), db: Session = Depends(get_db)):
    plan = db.get(ResearchPlan, plan_id)
    if not plan: raise HTTPException(404, "plan not found")
    if plan.status != "locked": raise HTTPException(409, "lock plan first")
    existing = db.scalar(select(PreregistrationArchive).where(PreregistrationArchive.plan_id == plan.id))
    if existing:
        return {"id": existing.id, "plan_id": plan.id, "archive_digest": existing.archive_digest, "archived_at": existing.archived_at.isoformat(), "note": "existing immutable server archive"}
    archive = {"farhp_server_archive_version":"1.0-rc.1", "plan":parse_json(plan.payload_json), "plan_id":plan.id, "study_id":plan.study_id, "revision":plan.revision, "archived_at":utcnow().isoformat(), "server_note":"server-side immutable database record; not an external trusted timestamp"}
    digest = sha256_hex(archive)
    row = PreregistrationArchive(plan_id=plan.id, archive_digest=digest, archive_json=canonical_json(archive), created_by_id=user.id)
    db.add(row); append_event(db, "plan", str(plan.id), "preregistration_archived", {"archive_digest":digest,"actor":user.username}); db.commit(); db.refresh(row)
    return {"id":row.id,"plan_id":plan.id,"archive_digest":digest,"archived_at":row.archived_at.isoformat(),"note":"server-side immutable database record; not an external trusted timestamp"}

@app.get("/api/plans/{plan_id}/archive")
def get_archive(plan_id: int, user: User = Depends(require_roles("principal_investigator","analyst")), db: Session = Depends(get_db)):
    row = db.scalar(select(PreregistrationArchive).where(PreregistrationArchive.plan_id == plan_id))
    if not row: raise HTTPException(404, "archive not found")
    return {"id":row.id,"plan_id":row.plan_id,"archive_digest":row.archive_digest,"archived_at":row.archived_at.isoformat(),"archive":parse_json(row.archive_json)}

@app.post("/api/plans/{plan_id}/invites")
def create_invite(plan_id: int, body: InviteCreateRequest, user: User = Depends(require_roles("principal_investigator","data_collector")), db: Session = Depends(get_db)):
    plan = db.get(ResearchPlan, plan_id)
    if not plan or plan.status != "locked": raise HTTPException(409, "locked plan required")
    code = secrets.token_urlsafe(12)
    expires = utcnow() + timedelta(hours=body.expires_in_hours) if body.expires_in_hours else None
    invite = Invite(code=code, plan_id=plan.id, created_by_id=user.id, max_uses=body.max_uses, expires_at=expires)
    db.add(invite); db.flush(); append_event(db, "plan", str(plan.id), "invite_created", {"invite_code_digest":sha256_hex(code),"max_uses":body.max_uses,"actor":user.username}); db.commit(); db.refresh(invite)
    return {"code":code,"plan_id":plan.id,"max_uses":invite.max_uses,"uses":invite.uses,"expires_at":invite.expires_at.isoformat() if invite.expires_at else None,"participant_url":f"/participant/{code}"}

@app.get("/api/invites/{code}/public")
def public_invite(code: str, db: Session = Depends(get_db)):
    invite = db.scalar(select(Invite).where(Invite.code == code))
    if not invite or not invite.is_active: raise HTTPException(404, "invite not found")
    if invite.expires_at and as_utc(invite.expires_at) < utcnow(): raise HTTPException(410, "invite expired")
    if invite.uses >= invite.max_uses: raise HTTPException(410, "invite exhausted")
    plan = invite.plan; payload = parse_json(plan.payload_json); consent = payload.get("governance",{}).get("consent_template",{})
    return {"study_id":plan.study_id,"plan_id":plan.id,"revision":plan.revision,"fingerprint":payload.get("plan_fingerprint"),"planned_sample_size":payload.get("planned_sample_size"),"design":payload.get("design"),"consent_template":consent,"remaining_uses":invite.max_uses-invite.uses}

@app.post("/api/invites/{code}/sessions")
def start_session(code: str, body: ConsentRequest, db: Session = Depends(get_db)):
    if not body.affirmative_consent or not body.eligibility_attestation:
        raise HTTPException(422, "affirmative consent and eligibility attestation required")
    invite = db.scalar(select(Invite).where(Invite.code == code))
    if not invite or not invite.is_active: raise HTTPException(404, "invite not found")
    if invite.expires_at and as_utc(invite.expires_at) < utcnow(): raise HTTPException(410, "invite expired")
    claim = db.execute(
        update(Invite)
        .where(Invite.id == invite.id, Invite.is_active.is_(True), Invite.uses < Invite.max_uses)
        .values(uses=Invite.uses + 1)
    )
    if claim.rowcount != 1:
        db.rollback()
        raise HTTPException(410, "invite exhausted")
    db.flush(); db.refresh(invite)
    participant_code = "P-" + secrets.token_hex(6).upper()
    session_id = "S-" + secrets.token_hex(12)
    plan_payload = parse_json(invite.plan.payload_json)
    consent = {"consented_at":utcnow().isoformat(),"affirmative_consent":True,"eligibility_attestation":True,"withdrawal_code_digest":sha256_hex(body.withdrawal_code),"consent_template":plan_payload.get("governance",{}).get("consent_template",{}),"plan_fingerprint":plan_payload.get("plan_fingerprint"),"direct_identifiers_collected":False}
    session = StudySession(session_id=session_id, plan_id=invite.plan_id, invite_id=invite.id, participant_code=participant_code, status="consented", consent_json=canonical_json(consent))
    db.add(session); db.flush(); append_event(db,"session",session_id,"consent_recorded",{"participant_pseudonym":pseudonym(participant_code),"plan_fingerprint":plan_payload.get("plan_fingerprint")}); db.commit(); db.refresh(session)
    return {"session_id":session_id,"participant_code":participant_code,"session_token":issue_session_token(session_id),"plan":plan_payload,"weblab_url":"/weblab/index.html?server_bridge=1"}

@app.get("/api/participant/sessions/{session_id}")
def participant_session(session_id: str, x_session_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    session = get_participant_session(session_id,x_session_token,db)
    return {"session_id":session.session_id,"participant_code":session.participant_code,"status":session.status,"plan":parse_json(session.plan.payload_json),"checkpoint":parse_json(session.checkpoint_json),"created_at":session.created_at.isoformat(),"updated_at":session.updated_at.isoformat()}

@app.put("/api/participant/sessions/{session_id}/checkpoint")
def save_checkpoint(session_id: str, body: CheckpointRequest, x_session_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    session = get_participant_session(session_id,x_session_token,db)
    if session.status == "completed": raise HTTPException(409, "session already completed")
    checkpoint = body.checkpoint
    if checkpoint.get("farhp_weblab_checkpoint_version") != "0.8": raise HTTPException(422, "v0.8 checkpoint required")
    if checkpoint.get("session",{}).get("session_id") and checkpoint["session"]["session_id"] != session_id:
        raise HTTPException(422, "checkpoint session_id mismatch")
    session.checkpoint_json=canonical_json(checkpoint); session.status="in_progress"; session.updated_at=utcnow(); append_event(db,"session",session_id,"checkpoint_saved",{"current_index":checkpoint.get("session",{}).get("current_index"),"saved_at":checkpoint.get("saved_at")}); db.commit()
    return {"ok":True,"updated_at":session.updated_at.isoformat()}

@app.post("/api/participant/sessions/{session_id}/complete")
def complete_session(session_id: str, body: CompleteRequest, x_session_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    session = get_participant_session(session_id,x_session_token,db)
    if session.status == "completed": return {"ok":True,"status":"already_completed"}
    study = body.study
    validate_schema(STUDY_SCHEMA,study,"study")
    plan_payload=parse_json(session.plan.payload_json)
    expected_fp=plan_payload.get("plan_fingerprint",{}).get("value")
    actual_fp=study.get("plan_fingerprint",{}).get("value")
    if expected_fp != actual_fp: raise HTTPException(422,"study plan fingerprint mismatch")
    if study.get("participant_id") != session.participant_code: raise HTTPException(422,"participant code mismatch")
    if study.get("study_id") != session.plan.study_id: raise HTTPException(422,"study_id mismatch")
    session.study_json=canonical_json(study);session.status="completed";session.completed_at=utcnow();session.updated_at=utcnow();append_event(db,"session",session_id,"study_completed",{"completed_at":session.completed_at.isoformat(),"trial_count":len(study.get("trials",[])),"audit_valid":study.get("audit_validation",{}).get("valid")});db.commit()
    return {"ok":True,"status":"completed","completed_at":session.completed_at.isoformat()}

@app.get("/api/sessions")
def list_sessions(user: User = Depends(require_roles("principal_investigator","data_collector","analyst")), db: Session = Depends(get_db)):
    raw = user.role in ("principal_investigator","data_collector")
    return [session_resource(s,raw=False if user.role=="analyst" else raw) for s in db.scalars(select(StudySession).order_by(StudySession.id.desc()))]

@app.get("/api/sessions/{session_id}")
def get_session_staff(session_id: str, user: User = Depends(require_roles("principal_investigator","data_collector","analyst")), db: Session = Depends(get_db)):
    session=db.scalar(select(StudySession).where(StudySession.session_id==session_id))
    if not session: raise HTTPException(404,"session not found")
    if user.role == "analyst":
        out=session_resource(session,raw=False)
        if session.study_json:
            study=parse_json(session.study_json); study["participant_id"]=pseudonym(session.participant_code); study["session_id"]=pseudonym(session.session_id,"SID"); study.get("governance",{}).pop("withdrawal_code",None); out["study"]=study
        return out
    return session_resource(session,raw=True)

@app.get("/api/plans/{plan_id}/audit")
def plan_audit(plan_id:int,user:User=Depends(require_roles("principal_investigator","data_collector","analyst")),db:Session=Depends(get_db)):
    events=events_for(db,"plan",str(plan_id));return {"verification":verify_events(events),"events":[{"index":e.event_index,"type":e.event_type,"payload":parse_json(e.payload_json),"prev_hash":e.prev_hash,"hash":e.event_hash,"created_at":e.created_at.isoformat()} for e in events]}

@app.get("/api/sessions/{session_id}/audit")
def session_audit(session_id:str,user:User=Depends(require_roles("principal_investigator","data_collector","analyst")),db:Session=Depends(get_db)):
    events=events_for(db,"session",session_id);return {"verification":verify_events(events),"events":[{"index":e.event_index,"type":e.event_type,"payload":parse_json(e.payload_json),"prev_hash":e.prev_hash,"hash":e.event_hash,"created_at":e.created_at.isoformat()} for e in events]}

@app.get("/api/analysis/summary")
def analysis_summary(user: User = Depends(require_roles("principal_investigator","analyst")), db: Session = Depends(get_db)):
    sessions=list(db.scalars(select(StudySession).where(StudySession.status=="completed")))
    total=correct=0; participants=set(); by_stimulus={}; by_condition={}; governance_failures=0
    for session in sessions:
        study=parse_json(session.study_json);participants.add(pseudonym(session.participant_code))
        if not study.get("audit_validation",{}).get("valid",False):governance_failures+=1
        condition=study.get("setup",{}).get("altered_condition") or study.get("plan",{}).get("design",{}).get("altered_condition","unknown")
        for trial in study.get("trials",[]):
            if trial.get("is_practice") or not trial.get("response"):continue
            total+=1;ok=bool(trial["response"].get("correct"));correct+=int(ok)
            key=trial.get("stimulus_key","unknown");rec=by_stimulus.setdefault(key,{"trials":0,"correct":0});rec["trials"]+=1;rec["correct"]+=int(ok)
            rec=by_condition.setdefault(condition,{"trials":0,"correct":0});rec["trials"]+=1;rec["correct"]+=int(ok)
    for group in (by_stimulus,by_condition):
        for rec in group.values():rec["accuracy"]=rec["correct"]/rec["trials"] if rec["trials"] else None;rec["wilson_95"]=wilson(rec["correct"],rec["trials"])
    return {"completed_sessions":len(sessions),"participants":len(participants),"formal_trials":total,"correct":correct,"accuracy":correct/total if total else None,"wilson_95":wilson(correct,total),"binomial_p_two_sided":exact_binomial_two_sided(correct,total),"governance_failures":governance_failures,"by_stimulus":by_stimulus,"by_condition":by_condition}

app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")
app.mount("/weblab", StaticFiles(directory=STATIC / "weblab", html=True), name="weblab")
