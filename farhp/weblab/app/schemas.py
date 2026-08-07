from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any

class LoginRequest(BaseModel):
    username: str
    password: str

class PlanImportRequest(BaseModel):
    payload: dict[str, Any]

class InviteCreateRequest(BaseModel):
    max_uses: int = Field(default=25, ge=1, le=10000)
    expires_in_hours: int | None = Field(default=168, ge=1, le=8760)

class ConsentRequest(BaseModel):
    affirmative_consent: bool
    eligibility_attestation: bool
    withdrawal_code: str = Field(min_length=6, max_length=80)

class CheckpointRequest(BaseModel):
    checkpoint: dict[str, Any]

class CompleteRequest(BaseModel):
    study: dict[str, Any]
