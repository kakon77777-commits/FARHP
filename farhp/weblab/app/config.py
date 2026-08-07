from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(x.strip() for x in os.getenv(name, default).split(",") if x.strip())


def env_json(name: str, default: dict[str, str]) -> dict[str, str]:
    raw = os.getenv(name)
    if not raw:
        return default
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return {str(k): str(v) for k, v in value.items()}


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("FARHP_ENV", "development")
    database_url: str = os.getenv("FARHP_DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'farhp_v10rc.sqlite3'}")
    secret_key: str = os.getenv("FARHP_SECRET_KEY", "farhp-v1.0-rc-demo-secret-change-me")
    token_max_age_seconds: int = int(os.getenv("FARHP_TOKEN_MAX_AGE", "43200"))
    demo_mode: bool = env_bool("FARHP_DEMO_MODE", True)
    local_auth_enabled: bool = env_bool("FARHP_LOCAL_AUTH_ENABLED", True)
    deidentification_salt: str = os.getenv("FARHP_DEIDENTIFICATION_SALT", "farhp-v1.0-rc-demo-deid-salt")
    auto_migrate: bool = env_bool("FARHP_AUTO_MIGRATE", True)
    allowed_hosts: tuple[str, ...] = env_list("FARHP_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
    force_https: bool = env_bool("FARHP_FORCE_HTTPS", False)
    hsts_seconds: int = int(os.getenv("FARHP_HSTS_SECONDS", "31536000"))
    csp_report_only: bool = env_bool("FARHP_CSP_REPORT_ONLY", False)
    db_pool_size: int = int(os.getenv("FARHP_DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("FARHP_DB_MAX_OVERFLOW", "10"))
    sqlite_busy_timeout_ms: int = int(os.getenv("FARHP_SQLITE_BUSY_TIMEOUT_MS", "30000"))
    oidc_enabled: bool = env_bool("FARHP_OIDC_ENABLED", False)
    oidc_issuer: str = os.getenv("FARHP_OIDC_ISSUER", "").rstrip("/")
    oidc_client_id: str = os.getenv("FARHP_OIDC_CLIENT_ID", "")
    oidc_client_secret: str = os.getenv("FARHP_OIDC_CLIENT_SECRET", "")
    oidc_redirect_uri: str = os.getenv("FARHP_OIDC_REDIRECT_URI", "http://127.0.0.1:8000/api/auth/oidc/callback")
    oidc_scope: str = os.getenv("FARHP_OIDC_SCOPE", "openid profile email")
    oidc_role_claim: str = os.getenv("FARHP_OIDC_ROLE_CLAIM", "groups")
    oidc_default_role: str = os.getenv("FARHP_OIDC_DEFAULT_ROLE", "analyst")
    oidc_role_map: dict[str, str] = None  # type: ignore[assignment]
    oidc_provider_label: str = os.getenv("FARHP_OIDC_PROVIDER_LABEL", "Institutional OIDC")
    app_name: str = "FARHP Research Server"
    app_version: str = "1.0.0-rc.1"

    def __post_init__(self):
        object.__setattr__(self, "oidc_role_map", env_json("FARHP_OIDC_ROLE_MAP", {
            "farhp-pi": "principal_investigator",
            "farhp-collector": "data_collector",
            "farhp-analyst": "analyst",
        }))

    @property
    def production(self) -> bool:
        return self.environment.lower() == "production"

    def validate(self) -> None:
        if self.production:
            if self.demo_mode:
                raise RuntimeError("FARHP_DEMO_MODE must be disabled in production")
            if len(self.secret_key) < 32 or "change-me" in self.secret_key:
                raise RuntimeError("FARHP_SECRET_KEY must be a unique secret of at least 32 characters")
            if len(self.deidentification_salt) < 32 or "demo" in self.deidentification_salt:
                raise RuntimeError("FARHP_DEIDENTIFICATION_SALT must be an independent secret")
            if "*" in self.allowed_hosts:
                raise RuntimeError("wildcard allowed hosts are not permitted in production")
        if self.oidc_enabled:
            missing = [name for name, value in {
                "FARHP_OIDC_ISSUER": self.oidc_issuer,
                "FARHP_OIDC_CLIENT_ID": self.oidc_client_id,
                "FARHP_OIDC_CLIENT_SECRET": self.oidc_client_secret,
                "FARHP_OIDC_REDIRECT_URI": self.oidc_redirect_uri,
            }.items() if not value]
            if missing:
                raise RuntimeError("OIDC enabled but missing: " + ", ".join(missing))
        if self.oidc_default_role not in {"principal_investigator", "data_collector", "analyst"}:
            raise RuntimeError("invalid FARHP_OIDC_DEFAULT_ROLE")


settings = Settings()
