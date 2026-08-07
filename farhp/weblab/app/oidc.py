from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urlencode
import hashlib
import re
import secrets
import httpx
import jwt
from fastapi import HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .models import User
from .security import unusable_password

state_serializer = URLSafeTimedSerializer(settings.secret_key, salt="farhp-oidc-state-v1")


async def fetch_json(url: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def post_form(url: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.post(url, data=data, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()


async def discovery() -> dict:
    if not settings.oidc_enabled:
        raise HTTPException(404, "OIDC is not enabled")
    document = await fetch_json(settings.oidc_issuer + "/.well-known/openid-configuration")
    if document.get("issuer", "").rstrip("/") != settings.oidc_issuer:
        raise HTTPException(502, "OIDC discovery issuer mismatch")
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
        if not document.get(key):
            raise HTTPException(502, f"OIDC discovery missing {key}")
    return document


def safe_return_to(value: str | None) -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"
    return value


async def authorization_url(return_to: str | None = None) -> str:
    document = await discovery()
    nonce = secrets.token_urlsafe(24)
    state = state_serializer.dumps({"nonce": nonce, "return_to": safe_return_to(return_to)})
    query = urlencode({
        "response_type": "code",
        "client_id": settings.oidc_client_id,
        "redirect_uri": settings.oidc_redirect_uri,
        "scope": settings.oidc_scope,
        "state": state,
        "nonce": nonce,
    })
    return document["authorization_endpoint"] + "?" + query


def parse_state(state: str) -> dict:
    try:
        value = state_serializer.loads(state, max_age=600)
        return {"nonce": str(value["nonce"]), "return_to": safe_return_to(value.get("return_to"))}
    except (BadSignature, SignatureExpired, KeyError) as exc:
        raise HTTPException(401, "invalid or expired OIDC state") from exc


def select_role(claims: dict) -> str:
    raw = claims.get(settings.oidc_role_claim, [])
    values = [raw] if isinstance(raw, str) else list(raw or [])
    for value in values:
        mapped = settings.oidc_role_map.get(str(value))
        if mapped:
            return mapped
    return settings.oidc_default_role


def safe_username(claims: dict, issuer: str, subject: str) -> str:
    candidate = claims.get("preferred_username") or claims.get("email") or claims.get("name")
    if candidate:
        candidate = str(candidate).split("@", 1)[0]
        candidate = re.sub(r"[^A-Za-z0-9_.-]+", "-", candidate).strip("-._")[:60]
    if not candidate:
        candidate = "oidc-" + hashlib.sha256(f"{issuer}|{subject}".encode()).hexdigest()[:16]
    return candidate


async def exchange_and_validate(code: str, state: str) -> tuple[dict, str]:
    state_data = parse_state(state)
    document = await discovery()
    token = await post_form(document["token_endpoint"], {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.oidc_redirect_uri,
        "client_id": settings.oidc_client_id,
        "client_secret": settings.oidc_client_secret,
    })
    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(401, "OIDC token response missing id_token")
    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")
    alg = header.get("alg")
    if not kid or not alg or alg == "none":
        raise HTTPException(401, "OIDC ID token header is invalid")
    jwks = await fetch_json(document["jwks_uri"])
    match = next((item for item in jwks.get("keys", []) if item.get("kid") == kid), None)
    if not match:
        raise HTTPException(401, "OIDC signing key not found")
    try:
        key = jwt.PyJWK.from_dict(match, algorithm=alg).key
        claims = jwt.decode(
            id_token,
            key=key,
            algorithms=[alg],
            audience=settings.oidc_client_id,
            issuer=settings.oidc_issuer,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, f"OIDC ID token validation failed: {exc}") from exc
    if claims.get("nonce") != state_data["nonce"]:
        raise HTTPException(401, "OIDC nonce mismatch")
    return claims, state_data["return_to"]


def upsert_oidc_user(db: Session, claims: dict) -> User:
    issuer = settings.oidc_issuer
    subject = str(claims["sub"])
    provider = "oidc:" + issuer
    user = db.scalar(select(User).where(User.auth_provider == provider, User.external_subject == subject))
    if user is None:
        base = safe_username(claims, issuer, subject)
        username = base
        suffix = 1
        while db.scalar(select(User.id).where(User.username == username)) is not None:
            suffix += 1
            username = f"{base[:72]}-{suffix}"
        user = User(
            username=username,
            password_hash=unusable_password(),
            role=select_role(claims),
            auth_provider=provider,
            external_subject=subject,
            email=claims.get("email"),
            display_name=claims.get("name"),
            is_active=True,
        )
        db.add(user)
        db.flush()
    else:
        user.role = select_role(claims)
        user.email = claims.get("email") or user.email
        user.display_name = claims.get("name") or user.display_name
    user.last_login_at = datetime.now(timezone.utc)
    return user
