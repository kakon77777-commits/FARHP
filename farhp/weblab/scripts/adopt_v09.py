"""Adopt an existing v0.9 create_all database into the Alembic migration chain."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alembic import command
from sqlalchemy import inspect
from app.db import engine
from app.migrations import alembic_config, upgrade_head, migration_status

required = {"users","research_plans","preregistration_archives","invites","study_sessions","audit_events"}
inspector = inspect(engine)
tables = set(inspector.get_table_names())
if "alembic_version" in tables:
    raise SystemExit("database already has Alembic metadata; use scripts/migrate.py")
missing = sorted(required - tables)
if missing:
    raise SystemExit("not a recognizable FARHP v0.9 database; missing: " + ", ".join(missing))
command.stamp(alembic_config(), "0001_v09_baseline")
upgrade_head()
print("FARHP v0.9 database adopted and upgraded:", migration_status())
