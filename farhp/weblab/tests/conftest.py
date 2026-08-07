import os, sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEST_DB = ROOT / 'data' / 'pytest_v10rc.sqlite3'
if TEST_DB.exists(): TEST_DB.unlink()
os.environ['FARHP_ENV'] = 'test'
os.environ['FARHP_DATABASE_URL'] = f'sqlite:///{TEST_DB}'
os.environ['FARHP_DEMO_MODE'] = '1'
os.environ['FARHP_AUTO_MIGRATE'] = '0'
os.environ['FARHP_SECRET_KEY'] = 'test-secret-that-is-long-enough-for-tests'
os.environ['FARHP_DEIDENTIFICATION_SALT'] = 'test-deid-salt-that-is-independent-long'
os.environ['FARHP_ALLOWED_HOSTS'] = 'testserver,farhp.local,localhost,127.0.0.1'

from app.main import app, seed_demo
from app.db import Base, SessionLocal
from app.migrations import upgrade_head

upgrade_head()

@pytest.fixture()
def client():
    with SessionLocal() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        seed_demo(db)
    with TestClient(app) as c:
        yield c
