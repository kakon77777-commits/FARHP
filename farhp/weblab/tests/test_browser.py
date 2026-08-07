import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def test_dashboard_browser_ui():
    html = (ROOT/'static/dashboard.html').read_text(encoding='utf-8')
    css = (ROOT/'static/assets/server.css').read_text(encoding='utf-8')
    js = "const sessionStorage={_:{},getItem(k){return this._[k]||null},setItem(k,v){this._[k]=String(v)},removeItem(k){delete this._[k]}};\n" + (ROOT/'static/assets/dashboard.js').read_text(encoding='utf-8')
    html = html.replace('<link rel="stylesheet" href="/assets/server.css">', f'<style>{css}</style>')
    html = html.replace('<script src="/assets/dashboard.js"></script>', '')
    html = html.replace('<head>', '<head><base href="http://farhp.local/">')
    demo = json.loads((ROOT/'examples/demo_plan_v0.8.json').read_text(encoding='utf-8'))
    plans=[]
    def handler(route):
        req=route.request; url=req.url; path=url.split('farhp.local',1)[-1]
        if path=='/assets/demo_plan_v0.8.json': return route.fulfill(json=demo)
        if path=='/api/health': return route.fulfill(json={'status':'ready','version':'1.0.0-rc.1','users':3,'migrations':{'up_to_date':True}})
        if path=='/api/auth/config': return route.fulfill(json={'local_auth_enabled':True,'oidc_enabled':False})
        if path=='/api/auth/login': return route.fulfill(json={'token':'demo-token','user':{'id':1,'username':'admin','role':'principal_investigator'}})
        if path=='/api/me': return route.fulfill(json={'id':1,'username':'admin','role':'principal_investigator'})
        if path=='/api/plans' and req.method=='GET': return route.fulfill(json=plans)
        if path=='/api/plans' and req.method=='POST':
            p={'id':1,'study_id':demo['study_id'],'revision':1,'status':'draft','fingerprint':None,'payload':{**demo,'status':'draft','plan_fingerprint':None}}
            plans[:] = [p]; return route.fulfill(json=p)
        if path=='/api/plans/1/lock':
            plans[0]['status']='locked';plans[0]['fingerprint']={'algorithm':'SHA-256','value':'a'*64};plans[0]['payload']['status']='locked';plans[0]['payload']['plan_fingerprint']=plans[0]['fingerprint'];return route.fulfill(json=plans[0])
        if path=='/api/plans/1/archive': return route.fulfill(json={'id':1,'plan_id':1,'archive_digest':'b'*64,'note':'server archive'})
        if path=='/api/plans/1/invites': return route.fulfill(json={'code':'INVITE-DEMO','participant_url':'/participant/INVITE-DEMO','max_uses':25})
        if path=='/api/plans/1/audit': return route.fulfill(json={'verification':{'valid':True,'event_count':3},'events':[]})
        if path=='/api/sessions': return route.fulfill(json=[])
        if path=='/api/analysis/summary': return route.fulfill(json={'participants':0,'formal_trials':0,'accuracy':None,'wilson_95':[None,None]})
        return route.fulfill(status=404,json={'detail':'mock route not found','path':path})
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[];page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None);page.on('pageerror',lambda e: errors.append(str(e)))
        page.route('**/*',handler)
        page.set_content(html,wait_until='load')
        page.add_script_tag(content=js)
        page.click('#loginBtn');page.wait_for_selector('#workspace:not([hidden])',timeout=5000)
        page.click('#demoPlanBtn');page.wait_for_timeout(100)
        page.locator('#plans button',has_text='鎖定').click();page.wait_for_timeout(100)
        page.locator('#plans button',has_text='封存').click();page.wait_for_timeout(100)
        page.locator('#plans button',has_text='建立邀請').click();page.wait_for_timeout(100)
        assert 'participant_url' in page.locator('#log').inner_text()
        (ROOT/'assets').mkdir(exist_ok=True)
        page.screenshot(path=ROOT/'assets/preview_v1.0_rc.png',full_page=True)
        assert not errors
        browser.close()
