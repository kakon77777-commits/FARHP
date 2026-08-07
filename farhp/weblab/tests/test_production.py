from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import base64, json, os, sqlite3, subprocess, sys
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy import inspect, select

ROOT = Path(__file__).resolve().parents[1]


def login(client, user='admin', password='FarhpAdmin!2026'):
    r = client.post('/api/auth/login', json={'username': user, 'password': password})
    assert r.status_code == 200, r.text
    return r.json()['token']


def auth(token): return {'Authorization': 'Bearer ' + token}

def demo_plan(): return json.loads((ROOT/'examples/demo_plan_v0.8.json').read_text())


def create_locked_invite(client, max_uses=5):
    t=login(client)
    plan=client.post('/api/plans',json={'payload':demo_plan()},headers=auth(t)).json()
    plan=client.post(f"/api/plans/{plan['id']}/lock",headers=auth(t)).json()
    invite=client.post(f"/api/plans/{plan['id']}/invites",json={'max_uses':max_uses,'expires_in_hours':1},headers=auth(t)).json()
    return invite


def test_security_headers_and_readiness(client):
    live=client.get('/api/health/live'); ready=client.get('/api/health/ready')
    assert live.status_code==200 and ready.status_code==200
    assert ready.json()['migrations']['up_to_date'] is True
    assert ready.json()['database']=='sqlite'
    assert live.headers['x-content-type-options']=='nosniff'
    assert live.headers['x-frame-options']=='DENY'
    assert "default-src 'self'" in live.headers['content-security-policy']
    assert live.headers['cache-control']=='no-store'
    assert len(live.headers['x-request-id'])>=16


def test_alembic_fresh_database(tmp_path):
    from alembic import command
    from alembic.config import Config
    db=tmp_path/'fresh.sqlite3'
    cfg=Config(str(ROOT/'alembic.ini'))
    cfg.set_main_option('script_location',str(ROOT/'migrations'))
    cfg.set_main_option('sqlalchemy.url',f'sqlite:///{db}')
    command.upgrade(cfg,'head')
    con=sqlite3.connect(db)
    try:
        tables={r[0] for r in con.execute("select name from sqlite_master where type='table'")}
        rev=con.execute('select version_num from alembic_version').fetchone()[0]
    finally: con.close()
    assert {'users','research_plans','study_sessions','audit_heads'} <= tables
    assert rev=='0002_v10rc_production'


def test_atomic_invite_capacity_under_concurrency(client):
    invite=create_locked_invite(client,max_uses=5)
    def start(i):
        return client.post(f"/api/invites/{invite['code']}/sessions",json={
            'affirmative_consent':True,
            'eligibility_attestation':True,
            'withdrawal_code':f'secret-{i:03d}',
        }).status_code
    with ThreadPoolExecutor(max_workers=10) as ex:
        codes=list(ex.map(start,range(12)))
    assert codes.count(200)==5, codes
    assert all(c in {200,410} for c in codes)


def test_sqlite_backup_restore_roundtrip(tmp_path):
    db=tmp_path/'source.sqlite3'
    con=sqlite3.connect(db);con.execute('create table marker(v text)');con.execute("insert into marker values ('original')");con.commit();con.close()
    out=tmp_path/'backups'
    env={**os.environ,'FARHP_DATABASE_URL':f'sqlite:///{db}','PYTHONPATH':str(ROOT)}
    r=subprocess.run([sys.executable,str(ROOT/'scripts/backup.py'),'--out',str(out)],env=env,text=True,capture_output=True)
    assert r.returncode==0,r.stderr
    backup=next(out.glob('*.sqlite3'))
    con=sqlite3.connect(db);con.execute("update marker set v='modified'");con.commit();con.close()
    r=subprocess.run([sys.executable,str(ROOT/'scripts/restore.py'),str(backup),'--confirm'],env=env,text=True,capture_output=True)
    assert r.returncode==0,r.stderr
    con=sqlite3.connect(db);value=con.execute('select v from marker').fetchone()[0];con.close()
    assert value=='original'


def test_postgres_backup_restore_commands_are_dry_runnable(tmp_path):
    env={**os.environ,'FARHP_DATABASE_URL':'postgresql+psycopg://u:p@db:5432/farhp','PYTHONPATH':str(ROOT)}
    r=subprocess.run([sys.executable,str(ROOT/'scripts/backup.py'),'--out',str(tmp_path),'--dry-run'],env=env,text=True,capture_output=True)
    assert r.returncode==0 and 'pg_dump' in r.stdout
    dummy=tmp_path/'x.dump';dummy.write_bytes(b'x')
    r=subprocess.run([sys.executable,str(ROOT/'scripts/restore.py'),str(dummy),'--dry-run'],env=env,text=True,capture_output=True)
    assert r.returncode==0 and 'pg_restore' in r.stdout


def _b64u(n: int) -> str:
    return base64.urlsafe_b64encode(n.to_bytes((n.bit_length()+7)//8,'big')).rstrip(b'=').decode()


def test_oidc_authorization_code_flow(client, monkeypatch):
    from app import oidc
    from app.config import settings
    from app.db import SessionLocal
    from app.models import User
    object.__setattr__(settings,'oidc_enabled',True)
    object.__setattr__(settings,'oidc_issuer','https://id.example.test')
    object.__setattr__(settings,'oidc_client_id','farhp-test')
    object.__setattr__(settings,'oidc_client_secret','secret')
    object.__setattr__(settings,'oidc_redirect_uri','http://testserver/api/auth/oidc/callback')
    object.__setattr__(settings,'oidc_role_map',{'farhp-pi':'principal_investigator'})
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    pub=key.public_key().public_numbers();kid='test-key'
    jwk={'kty':'RSA','kid':kid,'use':'sig','alg':'RS256','n':_b64u(pub.n),'e':_b64u(pub.e)}
    discovery={'issuer':settings.oidc_issuer,'authorization_endpoint':'https://id.example.test/auth','token_endpoint':'https://id.example.test/token','jwks_uri':'https://id.example.test/jwks'}
    state_box={}
    async def fake_fetch(url):
        return discovery if url.endswith('openid-configuration') else {'keys':[jwk]}
    async def fake_post(url,data):
        state_data=oidc.parse_state(state_box['state'])
        now=datetime.now(timezone.utc)
        claims={'iss':settings.oidc_issuer,'aud':settings.oidc_client_id,'sub':'subject-1','iat':now,'exp':now+timedelta(minutes=5),'nonce':state_data['nonce'],'preferred_username':'neo-researcher','email':'neo@example.test','groups':['farhp-pi']}
        return {'id_token':jwt.encode(claims,key,algorithm='RS256',headers={'kid':kid})}
    monkeypatch.setattr(oidc,'fetch_json',fake_fetch);monkeypatch.setattr(oidc,'post_form',fake_post)
    r=client.get('/api/auth/oidc/login?return_to=/',follow_redirects=False)
    assert r.status_code in {302,307}
    q=parse_qs(urlparse(r.headers['location']).query);state_box['state']=q['state'][0]
    r=client.get('/api/auth/oidc/callback',params={'code':'abc','state':state_box['state']},follow_redirects=False)
    assert r.status_code in {302,307} and '#token=' in r.headers['location']
    with SessionLocal() as db:
        user=db.scalar(select(User).where(User.external_subject=='subject-1'))
        assert user and user.role=='principal_investigator' and user.auth_provider.startswith('oidc:')
    object.__setattr__(settings,'oidc_enabled',False)
