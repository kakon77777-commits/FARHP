from pathlib import Path
import os, json, shutil
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/demo_generation.sqlite3'
if DB.exists(): DB.unlink()
os.environ.update(FARHP_DATABASE_URL=f'sqlite:///{DB}',FARHP_DEMO_MODE='1',FARHP_SECRET_KEY='demo-generation-secret',FARHP_DEIDENTIFICATION_SALT='demo-generation-deid')
from fastapi.testclient import TestClient
from app.main import app
OUT=ROOT/'examples/server_v0.9';shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True)
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
with TestClient(app) as c:
    login=c.post('/api/auth/login',json={'username':'admin','password':'FarhpAdmin!2026'}).json();h={'Authorization':'Bearer '+login['token']}
    source=json.loads((ROOT/'examples/demo_plan_v0.8.json').read_text())
    draft=c.post('/api/plans',json={'payload':source},headers=h).json();locked=c.post(f"/api/plans/{draft['id']}/lock",headers=h).json();archive=c.post(f"/api/plans/{draft['id']}/archive",headers=h).json();archive_full=c.get(f"/api/plans/{draft['id']}/archive",headers=h).json();invite=c.post(f"/api/plans/{draft['id']}/invites",json={'max_uses':5,'expires_in_hours':168},headers=h).json()
    public=c.get('/api/invites/'+invite['code']+'/public').json();started=c.post('/api/invites/'+invite['code']+'/sessions',json={'affirmative_consent':True,'eligibility_attestation':True,'withdrawal_code':'DEMO-WITHDRAW'}).json();sh={'X-Session-Token':started['session_token']}
    cp={'farhp_weblab_checkpoint_version':'0.8','saved_at':'2026-07-31T06:50:00Z','plan':started['plan'],'session':{'session_id':started['session_id'],'study_id':started['plan']['study_id'],'participant_id':started['participant_code'],'created_at':'2026-07-31T06:49:00Z','completed_at':None,'current_index':1,'on_break':False,'break_count':0,'governance':None,'audit_log':[],'trials':[]},'privacy_note':'demo lightweight checkpoint'}
    c.put(f"/api/participant/sessions/{started['session_id']}/checkpoint",json={'checkpoint':cp},headers=sh)
    study=json.loads((ROOT/'examples/demo_study_v0.8.json').read_text());study['session_id']=started['session_id'];study['participant_id']=started['participant_code'];study['study_id']=started['plan']['study_id'];study['plan']=started['plan'];study['plan_fingerprint']=started['plan']['plan_fingerprint'];study['governance']['consent_record']['plan_fingerprint']=started['plan']['plan_fingerprint']['value']
    complete=c.post(f"/api/participant/sessions/{started['session_id']}/complete",json={'study':study},headers=sh).json();summary=c.get('/api/analysis/summary',headers=h).json();plan_audit=c.get(f"/api/plans/{draft['id']}/audit",headers=h).json();session_audit=c.get(f"/api/sessions/{started['session_id']}/audit",headers=h).json();analyst=c.post('/api/auth/login',json={'username':'analyst','password':'Analyst!2026'}).json();analyst_session=c.get(f"/api/sessions/{started['session_id']}",headers={'Authorization':'Bearer '+analyst['token']}).json()
    safe_invite={k:v for k,v in invite.items() if k!='code'};safe_invite['code_digest_only']='demo package omits reusable raw invite code'
    safe_started={'session_id':started['session_id'],'participant_code':started['participant_code'],'plan':started['plan'],'note':'session token intentionally omitted'}
    for name,obj in [('plan_draft.json',draft),('plan_locked.json',locked),('archive_receipt.json',archive),('archive_full.json',archive_full),('invite_sanitized.json',safe_invite),('invite_public.json',public),('session_started_sanitized.json',safe_started),('checkpoint.json',cp),('study_completed.json',study),('completion_receipt.json',complete),('analysis_summary.json',summary),('plan_audit.json',plan_audit),('session_audit.json',session_audit),('analyst_deidentified_view.json',analyst_session)]:save(name,obj)
(OUT/'README.md').write_text('# FARHP Server v0.9 模擬協作流程\n\n全部資料由自動化測試產生，不是人類研究結果。原始邀請碼與 session token 未包含在示範包。\n',encoding='utf-8')
print(OUT)
