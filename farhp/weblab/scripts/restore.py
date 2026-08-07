from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, shutil, sqlite3, subprocess, sys
from sqlalchemy.engine import make_url
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

p=argparse.ArgumentParser();p.add_argument('backup');p.add_argument('--confirm',action='store_true');p.add_argument('--dry-run',action='store_true');args=p.parse_args()
backup=Path(args.backup)
if not backup.exists(): raise SystemExit('backup file not found')
manifest_path=backup.with_suffix(backup.suffix+'.manifest.json')
if manifest_path.exists():
    manifest=json.loads(manifest_path.read_text())
    if digest(backup)!=manifest.get('sha256'): raise SystemExit('backup SHA-256 mismatch')
if not args.confirm and not args.dry_run: raise SystemExit('restore is destructive; pass --confirm')
url=make_url(database_url);backend=url.get_backend_name()
if backend=='sqlite':
    target=Path(url.database or '')
    command=f'copy {backup} -> {target}'
    if args.dry_run: print(command);raise SystemExit
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists(): shutil.copy2(target,target.with_suffix(target.suffix+'.pre_restore'))
    src=sqlite3.connect(backup);dst=sqlite3.connect(target)
    try: src.backup(dst)
    finally: dst.close();src.close()
    check=sqlite3.connect(target)
    try:
        result=check.execute('PRAGMA integrity_check').fetchone()[0]
        if result!='ok': raise SystemExit('restored SQLite integrity check failed: '+result)
    finally: check.close()
else:
    cmd=['pg_restore','--clean','--if-exists','--no-owner','--dbname',database_url,str(backup)]
    if args.dry_run: print(' '.join(cmd));raise SystemExit
    subprocess.run(cmd,check=True)
print(json.dumps({'restored':str(backup),'backend':backend,'completed_at':datetime.now(timezone.utc).isoformat()},indent=2))
