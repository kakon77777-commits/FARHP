from __future__ import annotations
from pathlib import Path
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from .config import ROOT
from .db import engine, database_url


def alembic_config() -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return cfg


def upgrade_head() -> None:
    command.upgrade(alembic_config(), "head")


def current_revision() -> str | None:
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def head_revision() -> str:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def migration_status() -> dict[str, str | bool | None]:
    try:
        current = current_revision()
        head = head_revision()
        return {"current": current, "head": head, "up_to_date": current == head}
    except Exception as exc:
        return {"current": None, "head": None, "up_to_date": False, "error": str(exc)}
