from pathlib import Path
import json, wave, struct
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples'/'study_v0.6'
OUT.mkdir(parents=True,exist_ok=True)
html=(ROOT/'index.html').read_text(encoding='utf-8')
css=(ROOT/'styles.css').read_text(encoding='utf-8')
js=(ROOT/'app.js').read_text(encoding='utf-8')
js=js.replace("localStorage.getItem('farhp-theme') || 'dark'", "'dark'")
js=js.replace("localStorage.setItem('farhp-theme', root.dataset.theme);", "void 0;")
js=js.replace("document.addEventListener('DOMContentLoaded', init);", "init();")
html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>{css}</style>')
html=html.replace('<script src="app.js"></script>',f'<script>{js}</script>')
participants=[('P-DEMO-01',[True,True,True]),('P-DEMO-02',[True,False,True]),('P-DEMO-03',[False,True,False])]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content(html,wait_until='load')
    page.evaluate("() => { state.K=8; syllableState.duration=.18; utteranceState.speechRate=1.8; }")
    manifests=[]
    first_audio=None
    for idx,(pid,answers) in enumerate(participants):
        page.locator('#stimulusPool input').evaluate_all("els => els.forEach(el => { el.checked = ['nihao','nihaoma','yitianbuqu'].includes(el.value); })")
        page.fill('#studyId','FARHP-DEMO-v0.6')
        page.fill('#participantId',pid)
        page.locator('#studyRepeats').evaluate("el => { el.value='1'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.select_option('#practiceTrials','1')
        page.select_option('#breakEvery','0')
        page.locator('#experimentStrength').evaluate("el => { el.value='0.8'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.fill('#experimentSeed','20260731')
        page.select_option('#experimentCondition','alternating')
        page.click('#startExperimentBtn')
        page.wait_for_timeout(150)
        result=page.evaluate("""({answers,captureAudio}) => {
          const session=experimentState.session;
          let mainIndex=0;
          while(!session.completed_at){
            const t=currentExperimentTrial();
            t.play_counts={A:1,B:1,X:1};
            t.started_at_ms=Date.now()-(450+mainIndex*120);
            let answer=t.correct_answer;
            if(!t.is_practice){
              const shouldCorrect=answers[mainIndex++];
              if(!shouldCorrect) answer=t.correct_answer==='A'?'B':'A';
            }
            submitExperimentAnswer(answer);
            advanceExperimentTrial();
          }
          const manifest=experimentManifest();
          let audio=null;
          if(captureAudio){
            const s=session.stimulus_pool.nihao;
            audio={baseline:Array.from(s.audio.baseline),altered:Array.from(s.audio.altered),certificate:s.invariant_certificate,duration_seconds:s.duration_seconds};
          }
          return {manifest,audio};
        }""",{'answers':answers,'captureAudio':idx==0})
        manifests.append(result['manifest'])
        if result['audio'] is not None:first_audio=result['audio']
    group=page.evaluate("ms => mergeStudyManifests(ms)",manifests)
    group_csv=page.evaluate("g => groupAnalysisCsv(g)",group)
    browser.close()
for m in manifests:
    (OUT/f"study_{m['participant_id']}.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'group_analysis.json').write_text(json.dumps(group,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'group_analysis.csv').write_text(group_csv+'\n',encoding='utf-8')
(OUT/'SIMULATED_DATA_NOTICE.md').write_text('''# 模擬資料聲明\n\n此資料夾中的三份研究結果是自動化測試產生的**模擬受試者資料**，目的僅為驗證 FARHP WebLab v0.6 的多刺激順序、盲化紀錄、JSON Schema、群體合併與統計匯出。\n\n它們不是人類知覺實驗結果，不得用來主張 FARHP 已被人類受試者辨識或驗證。\n''',encoding='utf-8')

def write_wav(path,samples,sr=24000):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        frames=bytearray()
        for x in samples:
            v=max(-1,min(1,float(x)))
            frames += struct.pack('<h',int(round(v*32767)))
        w.writeframes(frames)
if first_audio:
    write_wav(OUT/'nihao_baseline.wav',first_audio['baseline'])
    write_wav(OUT/'nihao_alternating_080.wav',first_audio['altered'])
    (OUT/'nihao_pair_certificate.json').write_text(json.dumps({'duration_seconds':first_audio['duration_seconds'],'invariant_certificate':first_audio['certificate']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'participants':len(manifests),'main_trials':group['main_trials'],'accuracy':group['accuracy'],'p':group['binomial_two_sided_p']},ensure_ascii=False))
