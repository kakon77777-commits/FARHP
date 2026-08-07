'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'examples', 'experiments');
fs.mkdirSync(OUT, {recursive:true});
const code = fs.readFileSync(path.join(ROOT, 'app.js'), 'utf8');
const context = vm.createContext({
  console, Math, Number, Array, ArrayBuffer, DataView, Float32Array, Float64Array, Uint8Array, Blob, Date, JSON,
  setTimeout, clearTimeout,
  document:{querySelector:()=>null,querySelectorAll:()=>[],addEventListener:()=>{}}, window:{},
  localStorage:{getItem:()=>null,setItem:()=>{}}, URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},
  location:{hash:''}, requestAnimationFrame:()=>0,
});
vm.runInContext(code, context, {filename:'app.js'});
const ev = expr => vm.runInContext(expr, context);

(async () => {
  ev(`state.K=16;state.quantM=16;state.gain=.78;
      utteranceState.items=UTTERANCE_PRESETS.nihaoma.map(x=>({...normalizeUtteranceItem(x),duration:.42}));
      utteranceState.speechRate=1.15;utteranceState.sentenceType='question';utteranceState.intonationStrength=1;
      utteranceState.formantCoarticulation=true;utteranceState.coarticulation=true;utteranceState.overlapMs=28;`);
  const seed = 424242;
  const baseline = ev(`synthesizeUtteranceVariant('identity',1,${seed})`);
  const altered = ev(`synthesizeUtteranceVariant('zero',.8,${seed+104729})`);
  const sourceManifest = ev('utteranceManifest()');
  const invariant = {
    same_sample_count: baseline.samples.length === altered.samples.length,
    same_duration: Math.abs(baseline.duration-altered.duration)<1e-12,
    max_f0_track_difference_hz: ev('maxTrackDifference')(baseline.f0Track, altered.f0Track),
    same_lexical_bopomofo: JSON.stringify(baseline.lexical)===JSON.stringify(altered.lexical),
    same_surface_bopomofo: JSON.stringify(baseline.surface)===JSON.stringify(altered.surface),
    waveform_rms_difference: ev('waveformRmsDifference')(baseline.samples, altered.samples),
  };
  invariant.pass = invariant.same_sample_count && invariant.same_duration && invariant.max_f0_track_difference_hz<1e-9 && invariant.same_lexical_bopomofo && invariant.same_surface_bopomofo && invariant.waveform_rms_difference>1e-7;

  const responsePattern = [true, true, false, true];
  const trials = Array.from(ev(`makeBalancedAbxTrials(4,${seed})`), (t,i)=>{
    const correct = t.correct_answer;
    const answer = responsePattern[i] ? correct : (correct==='A'?'B':'A');
    return {...t,play_counts:{A:1+(i%2),B:1,X:1+(i===2?1:0)},started_at_ms:null,response:{answer,correct:answer===correct,rt_ms:820+i*310,submitted_at:new Date(Date.UTC(2026,6,27,2,0,i)).toISOString()}};
  });
  context._session = {
    session_id:'farhp-abx-example-424242',created_at:'2026-07-27T02:00:00.000Z',completed_at:'2026-07-27T02:01:10.000Z',
    task:'ABX_identity_match',seed,trial_count:4,altered_condition:'zero',altered_condition_label:'零相位',strength:.8,
    source_manifest:sourceManifest,invariant_certificate:invariant,audio:{baseline:baseline.samples,altered:altered.samples},trials
  };
  ev('experimentState.session = _session');
  const manifest = ev('experimentManifest()');
  const csv = ev('experimentCsv()');
  fs.writeFileSync(path.join(OUT,'demo_abx_session.json'), JSON.stringify(manifest,null,2));
  fs.writeFileSync(path.join(OUT,'demo_abx_session.csv'), csv);

  const t0=trials[0];
  const audio={baseline:baseline.samples,altered:altered.samples};
  for (const label of ['A','B','X']) {
    const condition=label==='A'?t0.a_condition:label==='B'?t0.b_condition:t0.x_condition;
    const blob=ev('encodeWav')(audio[condition], 24000);
    fs.writeFileSync(path.join(OUT,`trial01_${label}.wav`), Buffer.from(await blob.arrayBuffer()));
  }
  fs.writeFileSync(path.join(OUT,'README.md'), `# FARHP ABX 範例\n\n固定種子：\`424242\`。條件為目前語流 FARHP 與 80% 零相位介入。\n\n- \`trial01_A.wav\`、\`trial01_B.wav\`、\`trial01_X.wav\`：第一輪匿名刺激。\n- \`demo_abx_session.json\`：完整結果、條件映射與不變量證書。\n- \`demo_abx_session.csv\`：逐輪表格。\n\n此範例只驗證網站流程，不構成人類知覺研究結論。\n`);
  console.log('experiment example generated', invariant);
})().catch(err=>{console.error(err);process.exit(1);});
