import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def login(client,user='admin',password='FarhpAdmin!2026'):
    r=client.post('/api/auth/login',json={'username':user,'password':password});assert r.status_code==200,r.text;return r.json()['token']
def auth(token):return {'Authorization':'Bearer '+token}
def demo_plan():return json.loads((ROOT/'examples/demo_plan_v0.8.json').read_text())

def create_locked(client,token):
    r=client.post('/api/plans',json={'payload':demo_plan()},headers=auth(token));assert r.status_code==200,r.text
    pid=r.json()['id'];r=client.post(f'/api/plans/{pid}/lock',headers=auth(token));assert r.status_code==200,r.text
    return r.json()

def test_health_and_demo_users(client):
    r=client.get('/api/health');assert r.status_code==200;assert r.json()['users']==3

def test_login_and_me(client):
    t=login(client);r=client.get('/api/me',headers=auth(t));assert r.json()['role']=='principal_investigator'

def test_bad_login(client): assert client.post('/api/auth/login',json={'username':'x','password':'x'}).status_code==401

def test_analyst_cannot_create_plan(client):
    t=login(client,'analyst','Analyst!2026');assert client.post('/api/plans',json={'payload':demo_plan()},headers=auth(t)).status_code==403

def test_plan_import_lock_and_immutability(client):
    t=login(client);p=create_locked(client,t);assert len(p['fingerprint']['value'])==64;assert p['payload']['status']=='locked'
    assert client.post(f"/api/plans/{p['id']}/lock",headers=auth(t)).status_code==409

def test_archive_is_idempotent(client):
    t=login(client);p=create_locked(client,t);a=client.post(f"/api/plans/{p['id']}/archive",headers=auth(t));assert a.status_code==200
    b=client.post(f"/api/plans/{p['id']}/archive",headers=auth(t));assert b.json()['archive_digest']==a.json()['archive_digest']

def test_invite_requires_locked_plan(client):
    t=login(client);r=client.post('/api/plans',json={'payload':demo_plan()},headers=auth(t));pid=r.json()['id'];assert client.post(f'/api/plans/{pid}/invites',json={},headers=auth(t)).status_code==409

def start_participant(client):
    t=login(client);p=create_locked(client,t);inv=client.post(f"/api/plans/{p['id']}/invites",json={'max_uses':2,'expires_in_hours':24},headers=auth(t)).json();
    pub=client.get('/api/invites/'+inv['code']+'/public');assert pub.status_code==200
    r=client.post('/api/invites/'+inv['code']+'/sessions',json={'affirmative_consent':True,'eligibility_attestation':True,'withdrawal_code':'secret-123'});assert r.status_code==200,r.text
    return t,p,inv,r.json()

def test_consent_required(client):
    t=login(client);p=create_locked(client,t);inv=client.post(f"/api/plans/{p['id']}/invites",json={},headers=auth(t)).json();r=client.post('/api/invites/'+inv['code']+'/sessions',json={'affirmative_consent':False,'eligibility_attestation':True,'withdrawal_code':'secret'});assert r.status_code==422

def test_checkpoint_sync(client):
    _,_,_,s=start_participant(client);cp={'farhp_weblab_checkpoint_version':'0.8','saved_at':'2026-07-31T00:00:00Z','plan':s['plan'],'session':{'session_id':s['session_id'],'study_id':s['plan']['study_id'],'participant_id':s['participant_code'],'current_index':1,'trials':[]}}
    h={'X-Session-Token':s['session_token']};r=client.put(f"/api/participant/sessions/{s['session_id']}/checkpoint",json={'checkpoint':cp},headers=h);assert r.status_code==200,r.text
    d=client.get(f"/api/participant/sessions/{s['session_id']}",headers=h).json();assert d['checkpoint']['session']['current_index']==1

def test_wrong_session_token(client):
    _,_,_,s=start_participant(client);assert client.get(f"/api/participant/sessions/{s['session_id']}",headers={'X-Session-Token':'bad'}).status_code==401

def compatible_study(s):
    study=json.loads((ROOT/'examples/demo_study_v0.8.json').read_text())
    study['session_id']=s['session_id'];study['participant_id']=s['participant_code'];study['study_id']=s['plan']['study_id'];study['plan']=s['plan'];study['plan_fingerprint']=s['plan']['plan_fingerprint'];study['governance']['consent_record']['plan_fingerprint']=s['plan']['plan_fingerprint']['value']
    return study

def test_complete_study_and_analysis(client):
    t,_,_,s=start_participant(client);study=compatible_study(s);h={'X-Session-Token':s['session_token']};r=client.post(f"/api/participant/sessions/{s['session_id']}/complete",json={'study':study},headers=h);assert r.status_code==200,r.text
    a=client.get('/api/analysis/summary',headers=auth(t));assert a.status_code==200;assert a.json()['completed_sessions']==1

def test_complete_rejects_plan_mismatch(client):
    _,_,_,s=start_participant(client);study=compatible_study(s);study['plan_fingerprint']['value']='0'*64;h={'X-Session-Token':s['session_token']};assert client.post(f"/api/participant/sessions/{s['session_id']}/complete",json={'study':study},headers=h).status_code==422

def test_analyst_sees_pseudonyms(client):
    _,_,_,s=start_participant(client);a=login(client,'analyst','Analyst!2026');rows=client.get('/api/sessions',headers=auth(a)).json();assert rows[0]['participant_code'].startswith('PID-');assert rows[0]['participant_code']!=s['participant_code']

def test_audit_chains(client):
    t,p,_,s=start_participant(client);pa=client.get(f"/api/plans/{p['id']}/audit",headers=auth(t)).json();sa=client.get(f"/api/sessions/{s['session_id']}/audit",headers=auth(t)).json();assert pa['verification']['valid'];assert sa['verification']['valid']

def test_archive_retrieval(client):
    t=login(client);p=create_locked(client,t);client.post(f"/api/plans/{p['id']}/archive",headers=auth(t));r=client.get(f"/api/plans/{p['id']}/archive",headers=auth(t));assert r.status_code==200;assert r.json()['archive']['farhp_server_archive_version']=='1.0-rc.1'
