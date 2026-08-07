from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'styles.css').read_text(encoding='utf-8')
js = (ROOT / 'app.js').read_text(encoding='utf-8')

# set_content has no durable origin. Theme storage is bypassed; checkpoint code uses safe wrappers.
js = js.replace("localStorage.getItem('farhp-theme') || 'dark'", "'dark'")
js = js.replace("localStorage.setItem('farhp-theme', root.dataset.theme);", "void 0;")
js = js.replace("document.addEventListener('DOMContentLoaded', init);", "init();")
html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css}</style>')
html = html.replace('<script src="app.js"></script>', f'<script>{js}</script>')

errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1100}, device_scale_factor=1)
    page.on('console', lambda msg: errors.append(f'console:{msg.type}:{msg.text}') if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append(f'pageerror:{exc}'))
    page.set_content(html, wait_until='load')
    page.wait_for_timeout(400)
    page.evaluate("""() => {
      const memory = new Map();
      window.__farhpMemoryStorage = memory;
      safeStorageGet = key => memory.has(key) ? memory.get(key) : null;
      safeStorageSet = (key,value) => { memory.set(key,value); return true; };
      safeStorageRemove = key => { memory.delete(key); return true; };
    }""")

    # Core site and Mandarin pipeline still render.
    assert page.locator('#initialSelect option').count() == 22
    assert page.locator('#finalSelect option').count() == 37
    assert page.locator('#syllableDisplay').inner_text() == 'ㄇㄚˇ'
    page.select_option('#utterancePreset', 'yitianbuqu')
    page.wait_for_timeout(80)
    assert page.locator('#utteranceSurface').inner_text() == 'ㄧˋ　ㄊㄧㄢ　ㄅㄨˊ　ㄑㄩˋ'
    page.click('#runShiftTest')
    assert 'PASS' in page.locator('#shiftResult').inner_text()

    # Shorten synthesis for deterministic deployment tests.
    page.evaluate("() => { state.K=6; syllableState.duration=.11; utteranceState.speechRate=2.1; }")
    page.locator('#stimulusPool input').evaluate_all("els => els.forEach(el => { el.checked = ['nihao','nihaoma'].includes(el.value); })")
    page.fill('#studyId', 'FARHP-DEPLOY-TEST')
    page.fill('#participantId', 'P-BROWSER-01')
    page.fill('#plannedSampleSize', '12')
    page.fill('#preregistrationNote', 'Primary endpoint fixed before collection.')
    page.fill('#consentVersion', 'FARHP-CONSENT-TEST-v0.8')
    page.fill('#consentTitle', 'Test consent')
    page.fill('#consentSummary', 'Anonymous browser regression study.')
    page.locator('#studyRepeats').evaluate("el => { el.value='1'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    page.select_option('#practiceTrials', '1')
    page.select_option('#breakEvery', '1')
    page.locator('#experimentStrength').evaluate("el => { el.value='0.75'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    page.fill('#experimentSeed', '424242')
    page.select_option('#experimentCondition', 'zero')
    page.fill('#minRtMs', '150')
    page.fill('#maxRtMs', '30000')
    page.fill('#minCompletionRatio', '1')
    page.fill('#minValidTrialRatio', '0.8')

    # Lock plan and verify design controls are frozen with a deterministic fingerprint.
    plan = page.evaluate("async () => await lockResearchPlan()")
    assert plan['status'] == 'locked'
    assert len(plan['plan_fingerprint']['value']) == 64
    assert page.locator('#planLockBadge').inner_text() == '已鎖定'
    assert page.locator('#studyId').is_disabled()
    assert not page.locator('#startExperimentBtn').is_enabled()
    page.check('#eligibilityAttest')
    page.check('#consentAttest')
    page.click('#generateWithdrawalBtn')
    assert page.locator('#startExperimentBtn').is_enabled()

    # Build study, answer practice and first formal trial, then checkpoint and resume.
    page.click('#startExperimentBtn')
    page.wait_for_timeout(300)
    assert 'PASS' in page.locator('#experimentInvariant').inner_text()
    assert page.locator('#experimentProgress').inner_text() == '0 / 2'
    assert '練習' in page.locator('#experimentPhase').inner_text()

    checkpoint_result = page.evaluate("""() => {
      const practice=currentExperimentTrial();
      practice.play_counts={A:1,B:1,X:1}; practice.started_at_ms=Date.now()-420;
      submitExperimentAnswer(practice.correct_answer); advanceExperimentTrial();
      const first=currentExperimentTrial();
      first.play_counts={A:1,B:1,X:1}; first.started_at_ms=Date.now()-650;
      submitExperimentAnswer(first.correct_answer); advanceExperimentTrial();
      const breakTriggered=experimentState.session.on_break;
      persistCheckpoint();
      const raw=safeStorageGet(checkpointStorageKey());
      const cp=JSON.parse(raw);
      const savedIndex=cp.session.current_index;
      experimentState.session=null; experimentState.currentIndex=0;
      resumeFromCheckpoint(cp);
      return {
        version:cp.farhp_weblab_checkpoint_version,
        storageBytes:raw.length,
        savedIndex,
        restoredIndex:experimentState.currentIndex,
        restoredAnswered:experimentSummary().answered,
        breakTriggered,
        planFingerprint:cp.plan.plan_fingerprint.value,
        hasAudio:Object.prototype.hasOwnProperty.call(cp.session,'stimulus_pool')
      };
    }""")
    assert checkpoint_result['version'] == '0.8'
    assert checkpoint_result['storageBytes'] > 1000
    assert checkpoint_result['savedIndex'] == checkpoint_result['restoredIndex']
    assert checkpoint_result['restoredAnswered'] == 1
    assert checkpoint_result['breakTriggered'] is True
    assert checkpoint_result['hasAudio'] is False

    # Resume from the break, finish with one incorrect formal answer, and build hierarchy statistics.
    study_result = page.evaluate("""() => {
      advanceExperimentTrial();
      const second=currentExperimentTrial();
      second.play_counts={A:1,B:1,X:1}; second.started_at_ms=Date.now()-850;
      submitExperimentAnswer(second.correct_answer==='A'?'B':'A'); advanceExperimentTrial();
      const manifest=experimentManifest();
      const good=JSON.parse(JSON.stringify(manifest));
      good.participant_id='P-BROWSER-02'; good.session_id+='-GOOD';
      good.trials.forEach(t=>{if(!t.is_practice&&t.response){t.response.correct=true;t.response.rt_ms=700;}});
      const bad=JSON.parse(JSON.stringify(manifest));
      bad.participant_id='P-BROWSER-03'; bad.session_id+='-FAST';
      bad.trials.forEach(t=>{if(!t.is_practice&&t.response){t.response.correct=true;t.response.rt_ms=50;}});
      const group=mergeStudyManifests([manifest,good,bad]);
      experimentState.groupManifests=[manifest,good,bad]; experimentState.groupAnalysis=group; renderGroupAnalysis();
      return {
        studyVersion:manifest.farhp_weblab_study_version,
        planFingerprint:manifest.plan_fingerprint.value,
        completed:Boolean(manifest.completed_at),
        exclusionIncluded:manifest.exclusion_certificate.included,
        checkpointVersion:checkpointManifest().farhp_weblab_checkpoint_version,
        groupVersion:group.farhp_weblab_group_version,
        includedParticipants:group.participant_count,
        allParticipants:group.all_participant_count,
        excludedSessions:group.excluded_sessions,
        validTrials:group.main_trials,
        accuracy:group.accuracy,
        participantRows:group.by_participant.length,
        stimulusRows:group.by_stimulus.length,
        csvLines:groupAnalysisCsv(group).split('\\n').length,
        consentRecorded:Boolean(manifest.governance?.consent_record?.affirmative_consent),
        auditValid:manifest.audit_validation?.valid,
        auditEvents:manifest.audit_log?.length||0,
      };
    }""")
    page.wait_for_timeout(100)
    assert study_result['studyVersion'] == '0.8'
    assert len(study_result['planFingerprint']) == 64
    assert study_result['completed'] is True
    assert study_result['exclusionIncluded'] is True
    assert study_result['checkpointVersion'] == '0.8'
    assert study_result['groupVersion'] == '0.8'
    assert study_result['includedParticipants'] == 2
    assert study_result['allParticipants'] == 3
    assert study_result['excludedSessions'] == 1
    assert study_result['validTrials'] == 4
    assert abs(study_result['accuracy'] - 0.75) < 1e-12
    assert study_result['consentRecorded'] is True
    assert study_result['auditValid'] is True
    assert study_result['auditEvents'] >= 5
    assert study_result['participantRows'] == 3
    assert study_result['stimulusRows'] == 2
    assert page.locator('#groupExcluded').inner_text() == '1'
    assert page.locator('#participantAnalysisRows tr').count() == 3
    assert page.locator('#stimulusAnalysisRows tr').count() == 2
    assert page.locator('#experimentJsonBtn').is_enabled()
    assert page.locator('#checkpointExportBtn').is_enabled()

    # Save machine-readable examples from the tested runtime.
    examples = page.evaluate("async () => ({plan:researchPlanManifest(), checkpoint:checkpointManifest(), study:experimentManifest(), deidentified:await deidentifiedStudyManifest(), audit:await sealAuditArchive(), group:experimentState.groupAnalysis})")
    out = ROOT / 'examples' / 'governance_v0.8'
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in examples.items():
        (out / f'{name}.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

    page.locator('#experiment').screenshot(path=str(ROOT / 'assets' / 'preview_v0.8.png'))
    browser.close()

if errors:
    raise RuntimeError('\n'.join(errors))

print('FARHP WebLab browser test: PASS')
print({'checkpoint': checkpoint_result, 'study': study_result, 'console_errors': len(errors)})
