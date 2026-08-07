from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, shutil, sqlite3, subprocess
from sqlalchemy.engine import make_url
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.config import settings

def normalize(url: str) -> str:
    if url.startswith("postgres://"): return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"): return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url
database_url = normalize(settings.database_url)


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

p=argparse.ArgumentParser();p.add_argument('--out',default=str(ROOT/'backups'));p.add_argument('--dry-run',action='store_true');args=p.parse_args()
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
url=make_url(database_url);backend=url.get_backend_name()
if backend=='sqlite':
    source=Path(url.database or '')
    target=out/f'farhp_sqlite_{stamp}.sqlite3'
    if args.dry_run: print(target);raise SystemExit
    if not source.exists(): raise SystemExit(f'SQLite database not found: {source}')
    src=sqlite3.connect(source);dst=sqlite3.connect(target)
    try: src.backup(dst)
    finally: dst.close();src.close()
else:
    target=out/f'farhp_postgres_{stamp}.dump'
    cmd=['pg_dump','--format=custom','--no-owner','--file',str(target),database_url]
    if args.dry_run: print(' '.join(cmd));raise SystemExit
    subprocess.run(cmd,check=True)
manifest={'farhp_backup_version':'1.0-rc.1','created_at':datetime.now(timezone.utc).isoformat(),'backend':backend,'filename':target.name,'sha256':digest(target),'bytes':target.stat().st_size}
manifest_path=target.with_suffix(target.suffix+'.manifest.json');manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'backup':str(target),'manifest':str(manifest_path),**manifest},indent=2))
