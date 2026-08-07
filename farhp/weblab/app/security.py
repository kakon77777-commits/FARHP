from __future__ import annotations
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Header
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

ph = PasswordHasher()
serializer = URLSafeTimedSerializer(settings.secret_key, salt="farhp-auth-v1")
session_serializer = URLSafeTimedSerializer(settings.secret_key, salt="farhp-participant-v1")


def hash_password(password: str) -> str:
    return ph.hash(password)


def unusable_password() -> str:
    return "!oidc-managed-account!"


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def issue_user_token(user: User) -> str:
    return serializer.dumps({
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "token_version": user.token_version,
        "iat": datetime.now(timezone.utc).isoformat(),
    })


def issue_session_token(session_id: str) -> str:
    return session_serializer.dumps({"session_id": session_id})


def parse_session_token(token: str) -> str:
    try:
        data = session_serializer.loads(token, max_age=settings.token_max_age_seconds * 4)
        return str(data["session_id"])
    except (BadSignature, SignatureExpired, KeyError) as exc:
        raise HTTPException(status_code=401, detail="invalid or expired participant token") from exc


def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        data = serializer.loads(token, max_age=settings.token_max_age_seconds)
    except SignatureExpired as exc:
        raise HTTPException(status_code=401, detail="token expired") from exc
    except BadSignature as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    user = db.get(User, int(data.get("sub", 0)))
    if not user or not user.is_active or data.get("token_version") != user.token_version:
        raise HTTPException(status_code=401, detail="inactive or revoked user token")
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"role {user.role} not permitted")
        return user
    return dependency
