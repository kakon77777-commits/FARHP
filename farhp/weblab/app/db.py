from __future__ import annotations
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings


def normalized_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


database_url = normalized_database_url(settings.database_url)
is_sqlite = database_url.startswith("sqlite")
engine_options: dict = {"future": True, "pool_pre_ping": True}
if is_sqlite:
    engine_options["connect_args"] = {"check_same_thread": False, "timeout": settings.sqlite_busy_timeout_ms / 1000}
else:
    engine_options.update(pool_size=settings.db_pool_size, max_overflow=settings.db_max_overflow)

engine = create_engine(database_url, **engine_options)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute(f"PRAGMA busy_timeout={settings.sqlite_busy_timeout_ms}")
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_backend() -> str:
    return "sqlite" if is_sqlite else engine.url.get_backend_name()


def database_ping() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
