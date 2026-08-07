from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sqlalchemy import select
from app.db import Base,engine,SessionLocal
from app.models import User
from app.security import hash_password

parser=argparse.ArgumentParser(description='Create or update a FARHP staff user')
parser.add_argument('username')
parser.add_argument('role',choices=['principal_investigator','data_collector','analyst'])
parser.add_argument('--password',required=True)
args=parser.parse_args()
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    user=db.scalar(select(User).where(User.username==args.username))
    if user:
        user.role=args.role;user.password_hash=hash_password(args.password);user.is_active=True;action='updated'
    else:
        user=User(username=args.username,role=args.role,password_hash=hash_password(args.password));db.add(user);action='created'
    db.commit();print(f'{action}: {args.username} ({args.role})')
