from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config import settings
from app.migrations import upgrade_head, migration_status

if __name__ == "__main__":
    settings.validate()
    upgrade_head()
    status = migration_status()
    if not status.get("up_to_date"):
        raise SystemExit(f"migration failed: {status}")
    print(f"FARHP database migration OK: {status['current']}")
