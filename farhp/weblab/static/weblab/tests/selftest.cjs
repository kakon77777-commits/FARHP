'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const code = fs.readFileSync(require('path').join(__dirname, '..', 'app.js'), 'utf8');
const context = vm.createContext({
  console,
  Math,
  Number,
  Array,
  ArrayBuffer,
  DataView,
  Float32Array,
  Float64Array,
  Uint8Array,
  TextEncoder,
  crypto: require('crypto').webcrypto,
  Blob,
  Date,
  JSON,
  setTimeout,
  clearTimeout,
  document: { querySelector: () => null, querySelectorAll: () => [], addEventListener: () => {} },
  window: {},
  localStorage: { getItem: () => null, setItem: () => {} },
  URL: { createObjectURL: () => '', revokeObjectURL: () => {} },
  location: { hash: '' },
  requestAnimationFrame: () => 0,
});
vm.runInContext(code, context, { filename: 'app.js' });
const ev = expr => vm.runInContext(expr, context);
const near = (a, b, eps=1e-9) => assert.ok(Math.abs(a-b) <= eps, `${a} != ${b}`);

// wrap_phase belongs to (-pi, pi]. Numerical representation uses [-pi, pi).
for (const x of [-100, -Math.PI, -1, 0, 1, Math.PI, 100]) {
  const y = ev(`wrapPhase(${x})`);
  assert.ok(y >= -Math.PI - 1e-12 && y < Math.PI + 1e-12);
}
near(ev('circularDistance(Math.PI-0.01, -Math.PI+0.01)'), 0.02, 1e-9);

// Quantization must stay inside pi/M.
for (const M of [8,16,32,64]) {
  for (let i=0; i<1000; i++) {
    const x = -Math.PI + 2*Math.PI*i/999;
    const err = ev(`circularDistance(${x}, quantizePhase(${x}, ${M}).value)`);
    assert.ok(err <= Math.PI/M + 1e-9, `quantization bound failed M=${M}, err=${err}`);
  }
}

// Fundamental-anchored relative phase is invariant to a common time shift.
const f0=137.5, anchor=0.47, dt=0.0073;
for (let k=1; k<=32; k++) {
  const psi = k===1 ? 0 : Math.sin(k*0.37);
  const phi = k*anchor + psi;
  const shiftedPhi = phi - 2*Math.PI*k*f0*dt;
  const shiftedAnchor = anchor - 2*Math.PI*f0*dt;
  const recovered = k===1 ? 0 : ev(`wrapPhase(${shiftedPhi} - ${k} * ${shiftedAnchor})`);
  near(ev(`circularDistance(${recovered}, ${psi})`), 0, 1e-9);
}

// Synthesis and browser autocorrelation estimator form a controlled closed loop.
ev(`Object.assign(state, {f0: 125, duration: 0.5, K: 20, anchor: 0.35, gain: 0.8, quantM: 0});
state.amplitudes = Array.from({length:20}, (_,i)=>1/Math.pow(i+1,0.9));
state.phase = Array.from({length:20}, (_,i)=>i===0?0:wrapPhase(0.12*(i+1)));
state.audio = null;`);
const estimate = ev(`(() => { const s=synthesize().samples; return estimateF0(s.slice(1000, 3000), SAMPLE_RATE); })()`);
assert.ok(Math.abs(estimate.f0 - 125) < 1.0, `f0 estimate ${estimate.f0}`);
assert.ok(estimate.confidence > 0.7, `confidence ${estimate.confidence}`);



// Mandarin tone trajectories preserve their intended contour classes.
assert.ok(ev('toneF0(2, 1, 130)') > ev('toneF0(2, 0, 130)'), 'tone 2 must rise');
assert.ok(ev('toneF0(4, 1, 130)') < ev('toneF0(4, 0, 130)'), 'tone 4 must fall');
assert.ok(ev('toneF0(3, .56, 130)') < ev('toneF0(3, 0, 130)') && ev('toneF0(3, .56, 130)') < ev('toneF0(3, 1, 130)'), 'tone 3 must dip');
assert.ok(Math.abs(ev('toneF0(1, 1, 130)') - ev('toneF0(1, 0, 130)')) < 3, 'tone 1 must remain level');

// Coarse four-hu phonotactics reject category-incompatible combinations.
assert.strictEqual(ev("isSyllableCategoryAllowed('ㄐ','van')"), true);
assert.strictEqual(ev("isSyllableCategoryAllowed('ㄐ','a')"), false);
assert.strictEqual(ev("isSyllableCategoryAllowed('ㄍ','i')"), false);
assert.strictEqual(ev("isSyllableCategoryAllowed('ㄋ','v')"), true);
assert.strictEqual(ev("isSyllableCategoryAllowed('ㄓ','apical')"), true);

// Dynamic syllable synthesis must produce a finite non-silent waveform and tone metadata.
ev(`Object.assign(syllableState, {initial:'ㄇ', final:'a', tone:3, baseF0:132, duration:.72, residualStrength:.5, phaseStrength:1, phaseSource:'curved'});`);
const syllable = ev('synthesizeSyllable()');
assert.ok(syllable.samples.length > 10000, `syllable length ${syllable.samples.length}`);
assert.ok(syllable.samples.every(Number.isFinite), 'syllable samples must be finite');
assert.ok(Math.max(...syllable.samples.map(Math.abs)) > .2, 'syllable must be non-silent');
assert.ok(syllable.f0Min < syllable.f0Max, 'tone 3 must have f0 range');

// The syllable manifest keeps tone, FARHP and residual layers separate.
const manifest = ev('syllableManifest()');
assert.strictEqual(manifest.phonology.bopomofo, 'ㄇㄚˇ');
assert.strictEqual(manifest.phonology.tone, 3);
assert.ok(Array.isArray(manifest.farhp.values) && manifest.farhp.values.length > 5);
assert.ok(manifest.acoustics.f0_min_hz < manifest.acoustics.f0_max_hz);



// Third-tone sandhi keeps lexical tone separate from surface realization.
ev(`utteranceState.sandhi=true; utteranceState.neutralContext=true; utteranceState.declination=true; utteranceState.speechRate=1; utteranceState.finalLengthening=.18; utteranceState.coarticulation=true; utteranceState.overlapMs=32;
utteranceState.items=UTTERANCE_PRESETS.nihao.map(normalizeUtteranceItem);`);
let realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.lexicalTone), [3,3]);
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [2,3]);
assert.strictEqual(realized[0].sandhiApplied, true);

ev(`utteranceState.items=UTTERANCE_PRESETS.wohenhao.map(normalizeUtteranceItem);`);
realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [2,2,3]);

// Contextual neutral tone depends on the previous surface tone.
const neutralAfter3 = ev('neutralToneSemitones(3,.7)');
const neutralAfter4 = ev('neutralToneSemitones(4,.7)');
assert.ok(neutralAfter3 > neutralAfter4 + 5, `${neutralAfter3} vs ${neutralAfter4}`);

ev(`utteranceState.items=UTTERANCE_PRESETS.nihaoma.map(normalizeUtteranceItem);`);
realized = ev('realizeUtterance()');
assert.strictEqual(realized[2].surfaceTone, 0);
assert.strictEqual(realized[2].contextualNeutral, true);
assert.strictEqual(realized[2].contextPrevTone, 3);
assert.ok(realized[2].durationRealized < realized[1].durationRealized);

// Multi-syllable synthesis is finite and applies boundary overlap.
const utterance = ev('synthesizeUtterance()');
assert.strictEqual(utterance.realized.length, 3);
assert.ok(utterance.samples.length > 20000);
assert.ok(Array.from(utterance.samples.slice(0,2000)).every(Number.isFinite));
assert.ok(utterance.boundaries[1].overlap_samples > 0);
assert.ok(utterance.f0Max > utterance.f0Min);

// Utterance manifest preserves lexical/surface tones and per-syllable FARHP fields.
const utteranceManifestObj = ev('utteranceManifest()');
assert.deepStrictEqual(Array.from(utteranceManifestObj.syllables, x=>x.lexical_tone), [3,3,0]);
assert.deepStrictEqual(Array.from(utteranceManifestObj.syllables, x=>x.surface_tone), [2,3,0]);
assert.ok(utteranceManifestObj.syllables.every(x=>x.farhp && typeof x.farhp.source === 'string'));
assert.strictEqual(utteranceManifestObj.farhp_weblab_utterance_version, '0.6');


// Yi / bu sandhi is a separate surface-tone rewrite channel.
ev(`utteranceState.yiBuSandhi=true;utteranceState.prosodicGrouping=true;utteranceState.items=UTTERANCE_PRESETS.yigebuhaoma.map(normalizeUtteranceItem);`);
realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [2,4,4,3,0]);
assert.strictEqual(realized[0].yiBuSandhiApplied, true);
assert.strictEqual(realized[2].yiBuSandhiApplied, false);

ev(`utteranceState.items=UTTERANCE_PRESETS.yitianbuqu.map(normalizeUtteranceItem);`);
realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [4,1,2,4]);
assert.strictEqual(realized[0].yiBuSandhiApplied, true);
assert.strictEqual(realized[2].yiBuSandhiApplied, true);

// Prosodic boundaries block cross-group tone sandhi and create group identities.
ev(`utteranceState.items=UTTERANCE_PRESETS.grouped.map(normalizeUtteranceItem);utteranceState.prosodicGrouping=true;`);
realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [2,2,3,3,0]);
assert.deepStrictEqual(Array.from(realized, x=>x.prosodicGroup), [0,0,0,1,1]);
ev(`utteranceState.prosodicGrouping=false;`);
realized = ev('realizeUtterance()');
assert.deepStrictEqual(Array.from(realized, x=>x.surfaceTone), [2,2,2,3,0]);
ev(`utteranceState.prosodicGrouping=true;`);

// Sentence type produces an independent intonation layer.
ev(`utteranceState.items=UTTERANCE_PRESETS.nihaoma.map(normalizeUtteranceItem);utteranceState.sentenceType='question';utteranceState.intonationStrength=1;`);
realized = ev('realizeUtterance()');
assert.ok(realized.at(-1).prosodyEndSemi > 4, 'question must rise at sentence end');
ev(`utteranceState.sentenceType='declarative';`);
realized = ev('realizeUtterance()');
assert.ok(realized.at(-1).prosodyEndSemi < 0, 'declarative must fall slightly');

// Group boundaries insert silence and reset cross-syllable formant context.
ev(`utteranceState.items=UTTERANCE_PRESETS.grouped.map(normalizeUtteranceItem);utteranceState.sentenceType='question';utteranceState.groupPauseMs=90;utteranceState.formantCoarticulation=true;utteranceState.coarticulation=true;`);
const groupedUtterance = ev('synthesizeUtterance()');
assert.strictEqual(groupedUtterance.groupBoundaries.length, 1);
assert.ok(groupedUtterance.groupBoundaries[0].pause_samples > 2000);
const pause = groupedUtterance.groupBoundaries[0];
assert.ok(Array.from(groupedUtterance.f0Track.slice(pause.start_sample,pause.end_sample)).every(v=>v===0));
assert.strictEqual(groupedUtterance.realized[2].rightContextVowel, null);
assert.strictEqual(groupedUtterance.realized[3].leftContextVowel, null);
assert.ok(groupedUtterance.realized[0].rightContextVowel !== null);

// v0.4 manifest exposes the new rule and vocal-tract layers.
const v04Manifest = ev('utteranceManifest()');
assert.strictEqual(v04Manifest.farhp_weblab_utterance_version, '0.6');
assert.strictEqual(v04Manifest.rules.yi_bu_sandhi, true);
assert.strictEqual(v04Manifest.rules.prosodic_grouping, true);
assert.ok('vocal_tract_context' in v04Manifest.syllables[0]);
assert.strictEqual(v04Manifest.prosodic_groups.length, 1);


// Formant coarticulation changes the spectral envelope while preserving the f0 track.
ev(`utteranceState.items=UTTERANCE_PRESETS.nihao.map(normalizeUtteranceItem);utteranceState.formantCoarticulation=false;utteranceState.coarticulation=false;utteranceState.sentenceType='declarative';`);
const dry = ev('synthesizeUtterance()');
ev(`utteranceState.formantCoarticulation=true;`);
const wet = ev('synthesizeUtterance()');
assert.strictEqual(dry.samples.length, wet.samples.length);
let diffEnergy=0;
for(let i=0;i<dry.samples.length;i++) diffEnergy+=(dry.samples[i]-wet.samples[i])**2;
assert.ok(Math.sqrt(diffEnergy/dry.samples.length) > 1e-4, 'formant interpolation must change waveform');
assert.deepStrictEqual(Array.from(dry.f0Track), Array.from(wet.f0Track));


// FARHP-only experiment variants preserve the utterance timing and f0 trajectory.
ev(`state.K=12;utteranceState.items=UTTERANCE_PRESETS.nihaoma.map(x=>({...normalizeUtteranceItem(x),duration:.24}));utteranceState.speechRate=1.55;utteranceState.formantCoarticulation=true;utteranceState.coarticulation=true;utteranceState.sentenceType='question';`);
const experimentBaseline = ev("synthesizeUtteranceVariant('identity',1,20260727)");
const experimentZero = ev("synthesizeUtteranceVariant('zero',1,20260728)");
assert.strictEqual(experimentBaseline.samples.length, experimentZero.samples.length);
assert.deepStrictEqual(Array.from(experimentBaseline.f0Track), Array.from(experimentZero.f0Track));
assert.deepStrictEqual(Array.from(experimentBaseline.surface), Array.from(experimentZero.surface));
let phaseDiffEnergy = 0;
for (let i=0;i<experimentBaseline.samples.length;i++) phaseDiffEnergy += (experimentBaseline.samples[i]-experimentZero.samples[i])**2;
assert.ok(Math.sqrt(phaseDiffEnergy/experimentBaseline.samples.length) > 1e-4, 'phase intervention must change waveform');

// Fixed random seeds make random-phase experiment stimuli exactly reproducible.
const randomA = ev("synthesizeUtteranceVariant('random',.8,424242)");
const randomB = ev("synthesizeUtteranceVariant('random',.8,424242)");
const randomC = ev("synthesizeUtteranceVariant('random',.8,424243)");
assert.deepStrictEqual(Array.from(randomA.samples), Array.from(randomB.samples));
let seedDiff = 0;
for (let i=0;i<randomA.samples.length;i++) seedDiff += (randomA.samples[i]-randomC.samples[i])**2;
assert.ok(Math.sqrt(seedDiff/randomA.samples.length) > 1e-5, 'different seeds must change random-phase waveform');

// ABX summary keeps accuracy and response-time statistics separate from blinding.
ev(`experimentState.session={trials:[
 {play_counts:{A:1,B:2,X:1},response:{correct:true,rt_ms:900}},
 {play_counts:{A:2,B:1,X:3},response:{correct:false,rt_ms:1500}},
 {play_counts:{A:1,B:1,X:1},response:null}
]};`);
const expSummary = ev('experimentSummary()');
assert.strictEqual(expSummary.answered, 2);
assert.strictEqual(expSummary.correct, 1);
near(expSummary.accuracy, .5);
near(expSummary.medianRtMs, 1200);
assert.strictEqual(expSummary.totalReplays, 4);

// Balanced ABX randomization is deterministic and position-balanced.
const mapping1 = ev(`makeBalancedAbxTrials(8,777)`);
const mapping2 = ev(`makeBalancedAbxTrials(8,777)`);
assert.deepStrictEqual(JSON.parse(JSON.stringify(mapping1)), JSON.parse(JSON.stringify(mapping2)));
assert.strictEqual(Array.from(mapping1).filter(x=>x.a_condition==='baseline').length, 4);
assert.strictEqual(Array.from(mapping1).filter(x=>x.x_condition==='baseline').length, 4);
assert.strictEqual(Array.from(mapping1).filter(x=>x.correct_answer==='A').length, 4);


// Multi-stimulus ordering is deterministic, complete and participant-indexed.
const latinA = ev("latinStimulusOrder(['a','b','c','d'],1)");
const latinB = ev("latinStimulusOrder(['a','b','c','d'],1)");
assert.deepStrictEqual(Array.from(latinA), Array.from(latinB));
assert.deepStrictEqual(new Set(Array.from(latinA)).size, 4);
const plan = ev("buildStudyTrialPlan(['nihao','nihaoma','yitianbuqu','grouped'],2,2,'P-ALPHA',12345)");
assert.strictEqual(plan.trials.filter(x=>x.is_practice).length, 2);
assert.strictEqual(plan.trials.filter(x=>!x.is_practice).length, 8);
assert.strictEqual(new Set(Array.from(plan.orderedStimuli)).size, 4);

// Study summaries exclude practice trials from formal accuracy.
ev(`experimentState.session={trials:[
 {is_practice:true,play_counts:{A:1,B:1,X:1},response:{correct:false,rt_ms:500}},
 {is_practice:false,play_counts:{A:1,B:2,X:1},response:{correct:true,rt_ms:900}},
 {is_practice:false,play_counts:{A:2,B:1,X:3},response:{correct:false,rt_ms:1500}}
]};`);
const studySummary = ev('experimentSummary()');
assert.strictEqual(studySummary.practiceAnswered,1);
assert.strictEqual(studySummary.answered,2);
assert.strictEqual(studySummary.correct,1);
near(studySummary.accuracy,.5);

// Wilson interval and exact binomial test behave around chance.
const wilson = ev('wilsonInterval(50,100)');
assert.ok(wilson[0] < .5 && wilson[1] > .5);
const pChance = ev('binomialTwoSidedP(5,10,.5)');
assert.ok(pChance > .9 && pChance <= 1);
const pStrong = ev('binomialTwoSidedP(10,10,.5)');
assert.ok(pStrong < .01);

// Group merge excludes practice and groups by condition and stimulus.
const merged = ev(`mergeStudyManifests([
 {farhp_weblab_study_version:'0.6',session_id:'S-P1',study_id:'S',participant_id:'P1',setup:{altered_condition:'zero'},trials:[
  {is_practice:true,stimulus_key:'nihao',response:{correct:true,rt_ms:300}},
  {is_practice:false,stimulus_key:'nihao',response:{correct:true,rt_ms:700}},
  {is_practice:false,stimulus_key:'nihaoma',response:{correct:false,rt_ms:900}}]},
 {farhp_weblab_study_version:'0.6',session_id:'S-P2',study_id:'S',participant_id:'P2',setup:{altered_condition:'zero'},trials:[
  {is_practice:false,stimulus_key:'nihao',response:{correct:true,rt_ms:800}},
  {is_practice:false,stimulus_key:'nihaoma',response:{correct:true,rt_ms:1000}}]}
])`);
assert.strictEqual(merged.participant_count,2);
assert.strictEqual(merged.main_trials,4);
assert.strictEqual(merged.correct_trials,3);
near(merged.accuracy,.75);
assert.strictEqual(merged.by_condition_and_stimulus.length,2);

// v0.7 canonical plan serialization is key-order invariant.
assert.strictEqual(ev("stableStringify({b:2,a:{d:4,c:3}})"), ev("stableStringify({a:{c:3,d:4},b:2})"));

// Process exclusions never use accuracy and identify RT / playback failures explicitly.
const qualityFast = ev("trialQualityCertificate({play_counts:{A:1,B:1,X:1},response:{correct:true,rt_ms:50}},{...DEFAULT_EXCLUSION_POLICY,min_rt_ms:150})");
assert.strictEqual(qualityFast.included,false);
assert.ok(Array.from(qualityFast.reasons).includes('rt_too_fast'));
const qualityGood = ev("trialQualityCertificate({play_counts:{A:1,B:1,X:1},response:{correct:false,rt_ms:700}},DEFAULT_EXCLUSION_POLICY)");
assert.strictEqual(qualityGood.included,true);
assert.strictEqual(ev('DEFAULT_EXCLUSION_POLICY.accuracy_based_exclusion'),false);

// v0.7 aggregation applies embedded exclusion policies and creates participant/stimulus layers.
const mergedV07 = ev(`mergeStudyManifests([
 {farhp_weblab_study_version:'0.7',session_id:'V7-1',study_id:'V7',participant_id:'P1',setup:{altered_condition:'zero'},exclusion_policy:{...DEFAULT_EXCLUSION_POLICY},trials:[
  {sequence_index:1,is_practice:false,stimulus_key:'nihao',play_counts:{A:1,B:1,X:1},response:{correct:true,rt_ms:700}},
  {sequence_index:2,is_practice:false,stimulus_key:'nihaoma',play_counts:{A:1,B:1,X:1},response:{correct:false,rt_ms:900}}]},
 {farhp_weblab_study_version:'0.7',session_id:'V7-2',study_id:'V7',participant_id:'P2',setup:{altered_condition:'zero'},exclusion_policy:{...DEFAULT_EXCLUSION_POLICY},trials:[
  {sequence_index:1,is_practice:false,stimulus_key:'nihao',play_counts:{A:1,B:1,X:1},response:{correct:true,rt_ms:50}},
  {sequence_index:2,is_practice:false,stimulus_key:'nihaoma',play_counts:{A:1,B:1,X:1},response:{correct:true,rt_ms:50}}]}
])`);
assert.strictEqual(mergedV07.farhp_weblab_group_version,'0.8');
assert.strictEqual(mergedV07.participant_count,1);
assert.strictEqual(mergedV07.all_participant_count,2);
assert.strictEqual(mergedV07.excluded_sessions,1);
assert.strictEqual(mergedV07.main_trials,2);
assert.strictEqual(mergedV07.by_participant.length,2);
assert.strictEqual(mergedV07.by_stimulus.length,2);



// v0.8 live audit chains detect mutation and preserve order.
const auditChain = ev(`(() => {
  let prev='GENESIS'; const events=[];
  for (const [i,type] of ['plan_bound','consent_recorded','session_started'].entries()) {
    const event={index:i+1,timestamp:'2026-07-31T00:00:0'+i+'Z',type,payload:{n:i},prev_hash:prev};
    event.hash=liveDigest(prev,{index:event.index,timestamp:event.timestamp,type:event.type,payload:event.payload});
    events.push(event); prev=event.hash;
  }
  return events;
})()`);
assert.strictEqual(ev(`verifyLiveAuditChain(${JSON.stringify(auditChain)}).valid`), true);
const alteredAudit = JSON.parse(JSON.stringify(auditChain)); alteredAudit[1].payload.n=99;
assert.strictEqual(ev(`verifyLiveAuditChain(${JSON.stringify(alteredAudit)}).valid`), false);

// Governance quality review exposes missing consent, audit and invariant problems.
const qualityGov = ev(`qualityReviewManifests([{farhp_weblab_study_version:'0.8',session_id:'Q1',plan_fingerprint:{value:'${'a'.repeat(64)}'},governance:{consent_record:{affirmative_consent:true}},audit_validation:{valid:true},invariant_certificates:[{pass:true}]}])`);
assert.strictEqual(qualityGov.pass,true);
const qualityBad = ev(`qualityReviewManifests([{farhp_weblab_study_version:'0.8',session_id:'Q2',plan_fingerprint:{value:'bad'},governance:null,audit_validation:{valid:false},invariant_certificates:[{pass:false}]}])`);
assert.strictEqual(qualityBad.pass,false);
assert.strictEqual(qualityBad.missing_consent,1);
assert.strictEqual(qualityBad.audit_failures,1);

// Long-format analysis export excludes practice trials and keeps clustering keys.
const longRows = ev(`longFormatRows([{farhp_weblab_study_version:'0.8',study_id:'S',session_id:'SS',participant_id:'P',setup:{altered_condition:'zero'},trials:[{is_practice:true,response:{correct:true}},{is_practice:false,sequence_index:2,stimulus_key:'nihao',correct_answer:'A',response:{answer:'A',correct:true,rt_ms:700}}]}])`);
assert.strictEqual(longRows.length,1);
assert.strictEqual(longRows[0].participant_id,'P');
assert.ok(ev('R_ANALYSIS_SCRIPT.includes("glmer")'));
assert.ok(ev('PY_ANALYSIS_SCRIPT.includes("gee")'));
assert.ok(/^WD-[A-Z0-9]+$/.test(ev('makeWithdrawalCode()')));

// WAV writer emits a valid RIFF/WAVE header.
(async () => {
  const blob = ev(`encodeWav(synthesize().samples, SAMPLE_RATE)`);
  const buf = Buffer.from(await blob.arrayBuffer());
  assert.strictEqual(buf.subarray(0,4).toString('ascii'), 'RIFF');
  assert.strictEqual(buf.subarray(8,12).toString('ascii'), 'WAVE');
  assert.strictEqual(buf.subarray(36,40).toString('ascii'), 'data');
  const fp = await ev(`planFingerprint({z:1,a:[2,3]})`);
  assert.strictEqual(fp.value.length,64);
  assert.strictEqual(fp.algorithm,'SHA-256');
  console.log('FARHP WebLab self-test: 42 groups PASS');
})().catch(err => { console.error(err); process.exit(1); });
