'use strict';

const TAU = Math.PI * 2;
const SAMPLE_RATE = 24000;
const FORMANTS = {
  a: [[730, 100, 1.00], [1090, 140, 0.75], [2440, 180, 0.45]],
  i: [[270, 80, 1.00], [2290, 120, 0.80], [3010, 160, 0.35]],
  u: [[300, 90, 1.00], [870, 110, 0.75], [2240, 170, 0.35]],
  e: [[530, 90, 1.00], [1840, 130, 0.75], [2480, 170, 0.40]],
  o: [[570, 100, 1.00], [840, 120, 0.80], [2410, 180, 0.35]],
  y: [[310, 85, 1.00], [1750, 125, 0.78], [2450, 170, 0.36]],
  er: [[490, 100, 1.00], [1350, 150, 0.68], [1690, 190, 0.48]],
  apical: [[330, 100, 1.00], [1550, 170, 0.56], [2450, 220, 0.30]],
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const wrapPhase = (x) => ((x + Math.PI) % TAU + TAU) % TAU - Math.PI;
const circularDistance = (a, b) => Math.abs(wrapPhase(a - b));
const fmt = (v, digits = 3) => Number(v).toFixed(digits);

const state = {
  f0: 125,
  duration: 0.8,
  K: 24,
  anchor: 0.35,
  gain: 0.8,
  vowel: 'a',
  phasePreset: 'curved',
  strength: 1,
  quantM: 16,
  amplitudes: [],
  basePhase: [],
  targetPhase: [],
  phase: [],
  audio: null,
  audioCtx: null,
  source: null,
  analysis: null,
  baseline: null,
  randomSeed: 20260726,
};


const syllableState = {
  initial: 'ㄇ',
  final: 'ㄚ',
  tone: 3,
  baseF0: 132,
  duration: 0.78,
  residualStrength: 0.52,
  phaseStrength: 1,
  phaseSource: 'lab',
  audio: null,
  lastMeta: null,
  randomSeed: 20260727,
  contextPrevTone: null,
  prosodyStartSemi: 0,
  prosodyEndSemi: 0,
  leftContextVowel: null,
  rightContextVowel: null,
  formantCoarticulationStrength: 0,
};

const utteranceState = {
  items: [],
  preset: 'nihaoma',
  sandhi: true,
  yiBuSandhi: true,
  neutralContext: true,
  prosodicGrouping: true,
  coarticulation: true,
  formantCoarticulation: true,
  declination: true,
  sentenceType: 'question',
  intonationStrength: 1,
  speechRate: 1,
  overlapMs: 32,
  groupPauseMs: 90,
  finalLengthening: 0.18,
  audio: null,
  lastMeta: null,
};


const experimentState = {
  condition: 'zero',
  strength: 1,
  repeats: 1,
  practiceCount: 2,
  breakEvery: 8,
  seed: 20260731,
  studyId: 'FARHP-PERCEPT-v0.8',
  participantId: 'P-0001',
  selectedStimuli: ['nihao','nihaoma','yitianbuqu','grouped'],
  session: null,
  currentIndex: 0,
  groupAnalysis: null,
};

const EXPERIMENT_CONDITION_LABELS = {
  zero: '零相位',
  alternating: '奇偶交替相位',
  random: '固定隨機相位',
  curved: '曲面相位',
  identity: '目前語流 FARHP',
};

const STUDY_STIMULI = [
  {key:'nihao', label:'你好', bopomofo:'ㄋㄧˇ ㄏㄠˇ'},
  {key:'nihaoma', label:'你好嗎', bopomofo:'ㄋㄧˇ ㄏㄠˇ ˙ㄇㄚ'},
  {key:'wohenhao', label:'我很好', bopomofo:'ㄨㄛˇ ㄏㄣˇ ㄏㄠˇ'},
  {key:'mamahao', label:'媽媽好', bopomofo:'ㄇㄚ ˙ㄇㄚ ㄏㄠˇ'},
  {key:'yigebuhaoma', label:'一個不好嗎', bopomofo:'ㄧ ㄍㄜˋ ㄅㄨˋ ㄏㄠˇ ˙ㄇㄚ'},
  {key:'yitianbuqu', label:'一天不去', bopomofo:'ㄧ ㄊㄧㄢ ㄅㄨˋ ㄑㄩˋ'},
  {key:'grouped', label:'我很好｜你呢', bopomofo:'ㄨㄛˇ ㄏㄣˇ ㄏㄠˇ｜ㄋㄧˇ ˙ㄋㄜ'},
];
const STUDY_STIMULUS_MAP = Object.fromEntries(STUDY_STIMULI.map(x => [x.key,x]));

function mulberry32(seed) {
  return function rng() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function formantEnvelope(freq, formants) {
  let e = 0.02;
  for (const [center, bandwidth, gain] of formants) {
    const sigma = Math.max(bandwidth / 2.355, 1);
    e += gain * Math.exp(-0.5 * ((freq - center) / sigma) ** 2);
  }
  return e;
}

function makeAmplitudes(vowel, K, f0) {
  const arr = new Array(K);
  for (let i = 0; i < K; i++) {
    const k = i + 1;
    const env = vowel === 'flat' ? 1 : formantEnvelope(k * f0, FORMANTS[vowel]);
    arr[i] = env / Math.pow(k, 0.85);
  }
  const max = Math.max(...arr, 1e-9);
  return arr.map(v => v / max);
}

function phasePreset(name, K) {
  const p = new Array(K).fill(0);
  const rng = mulberry32(state.randomSeed);
  for (let i = 1; i < K; i++) {
    const k = i + 1;
    if (name === 'aligned') p[i] = 0;
    else if (name === 'curved') p[i] = wrapPhase(0.32 * Math.sqrt(k) + 0.075 * k * k / K);
    else if (name === 'alternating') p[i] = wrapPhase((k % 2) * Math.PI * 0.72 + 0.11 * k);
    else if (name === 'random') p[i] = -Math.PI + TAU * rng();
    else p[i] = state.phase[i] ?? 0;
  }
  return p;
}

function geodesicInterpolate(a, b, lambda) {
  return wrapPhase(a + lambda * wrapPhase(b - a));
}

function quantizePhase(x, M) {
  if (!M) return { value: wrapPhase(x), code: '∞' };
  const step = TAU / M;
  const code = ((Math.round((wrapPhase(x) + Math.PI) / step) % M) + M) % M;
  return { value: wrapPhase(-Math.PI + code * step), code };
}

function rebuildModel({ preserveCustom = false } = {}) {
  const oldAmp = state.amplitudes.slice();
  const oldPhase = state.phase.slice();
  state.amplitudes = makeAmplitudes(state.vowel, state.K, state.f0);
  if (preserveCustom) {
    for (let i = 0; i < Math.min(oldAmp.length, state.K); i++) state.amplitudes[i] = oldAmp[i];
  }
  state.basePhase = new Array(state.K).fill(0);
  state.targetPhase = phasePreset(state.phasePreset, state.K);
  state.phase = state.targetPhase.map((v, i) => geodesicInterpolate(state.basePhase[i], v, state.strength));
  if (state.phasePreset === 'custom' && preserveCustom) {
    for (let i = 0; i < Math.min(oldPhase.length, state.K); i++) state.phase[i] = oldPhase[i];
  }
  state.phase[0] = 0;
  updateAll();
}

function currentQuantizedPhase() {
  return state.phase.map((v, i) => i === 0 ? 0 : quantizePhase(v, state.quantM).value);
}

function synthesize() {
  const count = Math.max(1, Math.round(state.duration * SAMPLE_RATE));
  const out = new Float32Array(count);
  const phase = currentQuantizedPhase();
  const nyquist = SAMPLE_RATE / 2;
  for (let n = 0; n < count; n++) {
    const t = n / SAMPLE_RATE;
    let y = 0;
    for (let i = 0; i < state.K; i++) {
      const k = i + 1;
      if (k * state.f0 >= nyquist) break;
      y += state.amplitudes[i] * Math.cos(TAU * k * state.f0 * t + k * state.anchor + phase[i]);
    }
    out[n] = y;
  }
  let peak = 0;
  for (const v of out) peak = Math.max(peak, Math.abs(v));
  const scale = peak > 1e-9 ? state.gain / peak : 1;
  const fadeN = Math.min(Math.round(0.015 * SAMPLE_RATE), Math.floor(count / 4));
  for (let n = 0; n < count; n++) {
    let fade = 1;
    if (n < fadeN) fade = n / Math.max(1, fadeN);
    else if (n >= count - fadeN) fade = (count - 1 - n) / Math.max(1, fadeN);
    out[n] *= scale * clamp(fade, 0, 1);
  }
  state.audio = out;
  return { samples: out, rawPeak: peak };
}

async function playAudio() {
  stopAudio();
  const { samples } = synthesize();
  state.audioCtx ??= new (window.AudioContext || window.webkitAudioContext)({ sampleRate: SAMPLE_RATE });
  if (state.audioCtx.state === 'suspended') await state.audioCtx.resume();
  const buffer = state.audioCtx.createBuffer(1, samples.length, SAMPLE_RATE);
  buffer.copyToChannel(samples, 0);
  const source = state.audioCtx.createBufferSource();
  source.buffer = buffer;
  source.connect(state.audioCtx.destination);
  source.onended = () => { if (state.source === source) state.source = null; };
  source.start();
  state.source = source;
}

function stopAudio() {
  if (state.source) {
    try { state.source.stop(); } catch (_) {}
    state.source.disconnect();
    state.source = null;
  }
}

function setupCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.round(rect.width * dpr));
  const height = Math.max(1, Math.round(rect.height * dpr));
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, w: rect.width, h: rect.height };
}

function palette() {
  const cs = getComputedStyle(document.documentElement);
  return {
    text: cs.getPropertyValue('--text').trim(),
    muted: cs.getPropertyValue('--muted').trim(),
    line: cs.getPropertyValue('--line').trim(),
    accent: cs.getPropertyValue('--accent').trim(),
    accent2: cs.getPropertyValue('--accent-2').trim(),
    accent3: cs.getPropertyValue('--accent-3').trim(),
  };
}

function drawGrid(ctx, w, h, p) {
  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = p.line;
  ctx.lineWidth = 1;
  for (let i = 1; i < 5; i++) {
    const y = h * i / 5;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
  }
  for (let i = 1; i < 10; i++) {
    const x = w * i / 10;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
  }
}

function drawWave() {
  const canvas = $('#waveCanvas');
  const { ctx, w, h } = setupCanvas(canvas);
  const p = palette();
  drawGrid(ctx, w, h, p);
  const { samples, rawPeak } = synthesize();
  const showN = Math.min(samples.length, Math.round(0.04 * SAMPLE_RATE));
  ctx.strokeStyle = p.accent2;
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i < showN; i++) {
    const x = i / Math.max(1, showN - 1) * w;
    const y = h / 2 - samples[i] / Math.max(state.gain, 1e-6) * h * 0.43;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.fillStyle = p.muted;
  ctx.font = '12px sans-serif';
  ctx.fillText('0 ms', 8, h - 8);
  ctx.fillText('40 ms', w - 46, h - 8);
  $('#peakBadge').textContent = `Raw peak ${fmt(rawPeak, 2)}`;
}

function drawSpectrum() {
  const { ctx, w, h } = setupCanvas($('#spectrumCanvas'));
  const p = palette();
  ctx.clearRect(0, 0, w, h);
  const pad = { l: 34, r: 10, t: 12, b: 28 };
  const innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;
  ctx.strokeStyle = p.line; ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t + innerH); ctx.lineTo(w - pad.r, pad.t + innerH); ctx.stroke();
  const barW = innerW / state.K;
  for (let i = 0; i < state.K; i++) {
    const a = clamp(state.amplitudes[i], 0, 1.25);
    const bh = a / 1.25 * innerH;
    const grad = ctx.createLinearGradient(0, pad.t + innerH - bh, 0, pad.t + innerH);
    grad.addColorStop(0, p.accent);
    grad.addColorStop(1, p.accent2);
    ctx.fillStyle = grad;
    ctx.fillRect(pad.l + i * barW + 1, pad.t + innerH - bh, Math.max(1, barW - 2), bh);
  }
  ctx.fillStyle = p.muted; ctx.font = '11px sans-serif';
  ctx.fillText('Aₖ', 7, 16);
  ctx.fillText(`K=${state.K}`, w - 40, h - 7);
}

function drawPhaseWheel() {
  const { ctx, w, h } = setupCanvas($('#phaseCanvas'));
  const p = palette();
  ctx.clearRect(0, 0, w, h);
  const cx = w / 2, cy = h / 2, r = Math.min(w, h) * 0.36;
  ctx.strokeStyle = p.line; ctx.lineWidth = 1;
  for (const rr of [r * .35, r * .68, r]) { ctx.beginPath(); ctx.arc(cx, cy, rr, 0, TAU); ctx.stroke(); }
  for (let i = 0; i < 8; i++) { const a = i * TAU / 8; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + r * Math.cos(a), cy + r * Math.sin(a)); ctx.stroke(); }
  const q = currentQuantizedPhase();
  for (let i = 1; i < state.K; i++) {
    const angle = q[i];
    const rr = r * (0.38 + 0.62 * (i / Math.max(2, state.K - 1)));
    const x = cx + rr * Math.cos(angle), y = cy + rr * Math.sin(angle);
    ctx.fillStyle = i < 16 ? p.accent2 : p.accent;
    ctx.beginPath(); ctx.arc(x, y, i < 16 ? 3.3 : 2.1, 0, TAU); ctx.fill();
  }
  ctx.fillStyle = p.muted; ctx.font = '12px sans-serif';
  ctx.fillText('−π / π', cx - 18, cy + r + 18);
  ctx.fillText('0', cx + r + 7, cy + 4);
}

let heroT = 0;
function drawHero() {
  const canvas = $('#heroCanvas');
  if (!canvas) return;
  const { ctx, w, h } = setupCanvas(canvas);
  const p = palette();
  ctx.clearRect(0, 0, w, h);
  const cx = w / 2, cy = h / 2, maxR = Math.min(w, h) * .41;
  const phase = currentQuantizedPhase();
  for (let ring = 1; ring <= 5; ring++) {
    ctx.strokeStyle = p.line; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cx, cy, maxR * ring / 5, 0, TAU); ctx.stroke();
  }
  for (let i = 1; i < Math.min(state.K, 28); i++) {
    const k = i + 1;
    const a = phase[i] + heroT * (.15 + i * .004);
    const r = maxR * (.22 + .76 * i / Math.min(state.K, 28));
    const x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
    ctx.strokeStyle = i % 2 ? p.accent : p.accent2;
    ctx.globalAlpha = .2 + .6 * state.amplitudes[i];
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(x, y); ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.fillStyle = i % 2 ? p.accent : p.accent2;
    ctx.beginPath(); ctx.arc(x, y, 2 + 5 * state.amplitudes[i], 0, TAU); ctx.fill();
    if (i < 9) { ctx.fillStyle = p.muted; ctx.font = '11px sans-serif'; ctx.fillText(String(k), x + 7, y + 3); }
  }
  ctx.fillStyle = p.text; ctx.font = '800 56px sans-serif'; ctx.textAlign = 'center'; ctx.fillText('φ₁', cx, cy + 18); ctx.textAlign = 'start';
  heroT += .008;
  requestAnimationFrame(drawHero);
}

function renderHarmonicRows() {
  const tbody = $('#harmonicRows');
  tbody.textContent = '';
  const visible = Math.min(16, state.K);
  for (let i = 0; i < visible; i++) {
    const k = i + 1;
    const tr = document.createElement('tr');
    const q = quantizePhase(state.phase[i], state.quantM);
    tr.innerHTML = `
      <td>${k}</td>
      <td>${fmt(k * state.f0, 0)} Hz</td>
      <td><input class="amp-slider" data-i="${i}" type="range" min="0" max="1.25" step="0.005" value="${state.amplitudes[i]}"><output>${fmt(state.amplitudes[i], 2)}</output></td>
      <td>${i === 0 ? '<span class="muted">錨點</span>' : `<input class="phase-slider" data-i="${i}" type="range" min="-3.1416" max="3.1416" step="0.01" value="${state.phase[i]}"><output>${fmt(state.phase[i], 2)}</output>`}</td>
      <td><span class="phase-code">${i === 0 ? 'A' : q.code}</span></td>`;
    tbody.appendChild(tr);
  }
  $$('.amp-slider').forEach(el => el.addEventListener('input', e => {
    const i = Number(e.target.dataset.i);
    state.amplitudes[i] = Number(e.target.value);
    e.target.nextElementSibling.value = fmt(state.amplitudes[i], 2);
    updateVisualsOnly();
  }));
  $$('.phase-slider').forEach(el => el.addEventListener('input', e => {
    const i = Number(e.target.dataset.i);
    state.phasePreset = 'custom'; $('#phasePreset').value = 'custom';
    state.phase[i] = Number(e.target.value);
    e.target.nextElementSibling.value = fmt(state.phase[i], 2);
    updateVisualsOnly();
    renderHarmonicRows();
  }));
}

function quantMetrics() {
  if (!state.quantM) return { rmse: 0, max: 0, bound: 0 };
  const errors = state.phase.slice(1).map(v => circularDistance(v, quantizePhase(v, state.quantM).value));
  const rmse = Math.sqrt(errors.reduce((s, x) => s + x * x, 0) / Math.max(1, errors.length));
  return { rmse, max: Math.max(0, ...errors), bound: Math.PI / state.quantM };
}

function updateLabels() {
  $('#f0Out').value = `${fmt(state.f0, 0)} Hz`;
  $('#durationOut').value = `${fmt(state.duration, 2)} s`;
  $('#harmonicsOut').value = state.K;
  $('#anchorOut').value = `${fmt(state.anchor, 2)} rad`;
  $('#gainOut').value = `${Math.round(state.gain * 100)}%`;
  $('#strengthOut').value = fmt(state.strength, 2);
  $('#statF0').textContent = `${fmt(state.f0, 1)} Hz`;
  $('#statHarmonics').textContent = String(state.K);
  $('#statQuant').textContent = state.quantM ? `${state.quantM} 相` : '連續';
  const qm = quantMetrics();
  $('#statRmse').textContent = `${fmt(qm.rmse)} rad`;
}

function updateVisualsOnly() {
  updateLabels();
  drawWave(); drawSpectrum(); drawPhaseWheel();
  if ($('#initialSelect')?.options?.length && syllableState.phaseSource === 'lab') updateSyllableUI();
}

function updateAll() {
  updateLabels(); renderHarmonicRows(); drawWave(); drawSpectrum(); drawPhaseWheel();
  runQuantTest(false);
  if ($('#initialSelect')?.options?.length && syllableState.phaseSource === 'lab') updateSyllableUI();
}

function toast(message) {
  const el = $('#toast');
  el.textContent = message; el.classList.add('show');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove('show'), 2600);
}

function objectUrlDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function encodeWav(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const write = (off, s) => [...s].forEach((c, i) => view.setUint8(off + i, c.charCodeAt(0)));
  write(0, 'RIFF'); view.setUint32(4, 36 + samples.length * 2, true); write(8, 'WAVE'); write(12, 'fmt ');
  view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true); view.setUint32(28, sampleRate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
  write(36, 'data'); view.setUint32(40, samples.length * 2, true);
  let o = 44;
  for (const x of samples) { view.setInt16(o, Math.round(clamp(x, -1, 1) * 32767), true); o += 2; }
  return new Blob([buffer], { type: 'audio/wav' });
}

function specObject() {
  const q = currentQuantizedPhase();
  return {
    farhp_weblab_version: '0.2',
    generated_at: new Date().toISOString(),
    synthesis: { sample_rate_hz: SAMPLE_RATE, duration_sec: state.duration, f0_hz: state.f0, anchor_phase_rad: state.anchor, gain: state.gain, vowel_preset: state.vowel },
    phase: { representation: 'angle_rad', quantization_bins: state.quantM, preset: state.phasePreset, strength: state.strength, harmonic_indices: Array.from({ length: state.K - 1 }, (_, i) => i + 2), values: q.slice(1), continuous_values: state.phase.slice(1) },
    harmonics: { indices: Array.from({ length: state.K }, (_, i) => i + 1), amplitude: state.amplitudes.slice() },
    formula: 'psi_k = wrap(phi_k - k*phi_1)',
    scope: 'harmonic periodic synthesis MVP; not a complete speech vocoder',
  };
}

function loadSpec(obj) {
  const syn = obj.synthesis ?? obj.analysis ?? {};
  const phase = obj.phase ?? {};
  const harmonics = obj.harmonics ?? {};
  const amp = harmonics.amplitude ?? obj.amplitudes;
  const vals = phase.continuous_values ?? phase.values ?? obj.farhp_rad;
  if (!Array.isArray(amp) || !Array.isArray(vals)) throw new Error('JSON 缺少 harmonics.amplitude 或 phase.values');
  state.K = amp.length;
  state.f0 = Number(syn.f0_hz ?? state.f0);
  state.duration = Number(syn.duration_sec ?? state.duration);
  state.anchor = Number(syn.anchor_phase_rad ?? obj.anchor?.phase_rad ?? state.anchor);
  state.gain = Number(syn.gain ?? state.gain);
  state.vowel = syn.vowel_preset ?? 'flat';
  state.phasePreset = 'custom'; state.strength = 1;
  state.quantM = Number(phase.quantization_bins ?? 0);
  state.amplitudes = amp.map(Number);
  state.phase = vals.length === state.K ? vals.map(Number) : [0, ...vals.map(Number)];
  state.phase[0] = 0;
  state.basePhase = new Array(state.K).fill(0); state.targetPhase = state.phase.slice();
  syncControls(); updateAll();
}

function syncControls() {
  $('#f0').value = clamp(state.f0, 70, 320);
  $('#duration').value = clamp(state.duration, .2, 2);
  $('#harmonics').value = clamp(state.K, 4, 48);
  $('#anchor').value = clamp(state.anchor, -Math.PI, Math.PI);
  $('#gain').value = clamp(state.gain, .05, 1);
  $('#vowelPreset').value = FORMANTS[state.vowel] || state.vowel === 'flat' ? state.vowel : 'flat';
  $('#phasePreset').value = state.phasePreset;
  $('#strength').value = state.strength;
  $('#quantization').value = String(state.quantM);
}

function parseWav(arrayBuffer) {
  const view = new DataView(arrayBuffer);
  const str = (o, n) => Array.from({ length: n }, (_, i) => String.fromCharCode(view.getUint8(o + i))).join('');
  if (str(0, 4) !== 'RIFF' || str(8, 4) !== 'WAVE') throw new Error('不是有效的 RIFF/WAVE 檔');
  let offset = 12, fmtChunk = null, dataOffset = 0, dataSize = 0;
  while (offset + 8 <= view.byteLength) {
    const id = str(offset, 4); const size = view.getUint32(offset + 4, true); const start = offset + 8;
    if (id === 'fmt ') fmtChunk = { format: view.getUint16(start, true), channels: view.getUint16(start + 2, true), sampleRate: view.getUint32(start + 4, true), bits: view.getUint16(start + 14, true) };
    if (id === 'data') { dataOffset = start; dataSize = size; break; }
    offset = start + size + (size % 2);
  }
  if (!fmtChunk || !dataOffset) throw new Error('WAV 缺少 fmt 或 data 區塊');
  const { format, channels, sampleRate, bits } = fmtChunk;
  if (![1, 3].includes(format)) throw new Error(`目前只支援 PCM/IEEE float WAV（格式 ${format}）`);
  const bytes = bits / 8; const frames = Math.floor(dataSize / (bytes * channels)); const samples = new Float32Array(frames);
  const readSample = (o) => {
    if (format === 3 && bits === 32) return view.getFloat32(o, true);
    if (bits === 8) return (view.getUint8(o) - 128) / 128;
    if (bits === 16) return view.getInt16(o, true) / 32768;
    if (bits === 24) { let x = view.getUint8(o) | view.getUint8(o + 1) << 8 | view.getUint8(o + 2) << 16; if (x & 0x800000) x |= 0xff000000; return x / 8388608; }
    if (bits === 32) return view.getInt32(o, true) / 2147483648;
    throw new Error(`不支援 ${bits}-bit WAV`);
  };
  for (let i = 0; i < frames; i++) {
    let sum = 0;
    for (let c = 0; c < channels; c++) sum += readSample(dataOffset + (i * channels + c) * bytes);
    samples[i] = sum / channels;
  }
  return { sampleRate, samples, channels, bits };
}

function hann(n, N) { return N <= 1 ? 1 : 0.5 - 0.5 * Math.cos(TAU * n / (N - 1)); }

function estimateF0(samples, sr, minHz = 60, maxHz = 400) {
  const maxLag = Math.min(Math.floor(sr / minHz), samples.length - 2);
  const minLag = Math.max(2, Math.floor(sr / maxHz));
  let mean = 0; for (const x of samples) mean += x; mean /= samples.length;
  const x = new Float64Array(samples.length); let energy = 0;
  for (let i = 0; i < samples.length; i++) { x[i] = (samples[i] - mean) * hann(i, samples.length); energy += x[i] * x[i]; }
  if (energy < 1e-9) throw new Error('框架能量太低，無法估計基頻');
  const corr = new Float64Array(maxLag + 1);
  let bestLag = minLag, best = -Infinity;
  for (let lag = minLag; lag <= maxLag; lag++) {
    let s = 0, a = 0, b = 0;
    for (let i = 0; i < x.length - lag; i++) { const u = x[i], v = x[i + lag]; s += u * v; a += u * u; b += v * v; }
    corr[lag] = s / Math.sqrt(Math.max(a * b, 1e-16));
    if (corr[lag] > best) { best = corr[lag]; bestLag = lag; }
  }
  if (bestLag > minLag && bestLag < maxLag) {
    const ym = corr[bestLag - 1], y0 = corr[bestLag], yp = corr[bestLag + 1];
    const denom = ym - 2 * y0 + yp;
    if (Math.abs(denom) > 1e-9) bestLag += 0.5 * (ym - yp) / denom;
  }
  return { f0: sr / bestLag, confidence: clamp(best, 0, 1) };
}

function analyzeHarmonics(samples, sr, f0, K) {
  const N = samples.length; let mean = 0; for (const x of samples) mean += x; mean /= N;
  const coeffs = [], amps = [], phases = [];
  let windowSum = 0; for (let n = 0; n < N; n++) windowSum += hann(n, N);
  for (let k = 1; k <= K; k++) {
    if (k * f0 >= sr / 2) break;
    let re = 0, im = 0;
    for (let n = 0; n < N; n++) {
      const x = (samples[n] - mean) * hann(n, N);
      const a = TAU * k * f0 * n / sr;
      re += x * Math.cos(a); im -= x * Math.sin(a);
    }
    const c = { re, im }; coeffs.push(c);
    amps.push(2 * Math.hypot(re, im) / Math.max(windowSum, 1));
    phases.push(Math.atan2(im, re));
  }
  const maxAmp = Math.max(...amps, 1e-9); const normalized = amps.map(v => v / maxAmp);
  const anchor = phases[0] ?? 0;
  const farhp = phases.map((phi, i) => i === 0 ? 0 : wrapPhase(phi - (i + 1) * anchor));
  const threshold = maxAmp * 0.025;
  const mask = amps.map(v => v >= threshold);
  return { amplitudes: normalized, rawAmplitudes: amps, phases, farhp, anchor, mask, valid: mask.filter(Boolean).length };
}

async function analyzeWavFile(file) {
  $('#analysisState').textContent = '分析中'; $('#analysisState').className = 'status-badge neutral';
  try {
    const wav = parseWav(await file.arrayBuffer());
    const frameSec = Math.min(0.08, wav.samples.length / wav.sampleRate);
    const frameN = Math.min(wav.samples.length, Math.max(256, Math.round(frameSec * wav.sampleRate)));
    const center = Math.floor(wav.samples.length / 2); const start = clamp(center - Math.floor(frameN / 2), 0, wav.samples.length - frameN);
    const frame = wav.samples.slice(start, start + frameN);
    const f0est = estimateF0(frame, wav.sampleRate);
    const maxK = Math.min(48, Math.floor((wav.sampleRate / 2 - 1) / f0est.f0));
    const h = analyzeHarmonics(frame, wav.sampleRate, f0est.f0, maxK);
    const grade = f0est.confidence > .82 && h.valid >= 10 ? 4 : f0est.confidence > .65 && h.valid >= 6 ? 3 : f0est.confidence > .45 ? 2 : 1;
    state.analysis = { fileName: file.name, sampleRate: wav.sampleRate, duration: wav.samples.length / wav.sampleRate, frameStart: start / wav.sampleRate, frameLength: frameN / wav.sampleRate, f0: f0est.f0, confidence: f0est.confidence, grade, ...h };
    $('#aSampleRate').textContent = `${wav.sampleRate} Hz / ${wav.bits}-bit`;
    $('#aF0').textContent = `${fmt(f0est.f0, 2)} Hz`;
    $('#aConfidence').textContent = fmt(f0est.confidence, 3);
    $('#aHarmonics').textContent = `${h.valid}/${h.amplitudes.length}`;
    $('#aFrameTime').textContent = `${fmt(start / wav.sampleRate, 3)}–${fmt((start + frameN) / wav.sampleRate, 3)} s`;
    $('#aGrade').textContent = `Γ=${grade}`;
    $('#analysisState').textContent = '完成'; $('#analysisState').className = 'status-badge';
    $('#useAnalysisBtn').disabled = false; $('#analysisJsonBtn').disabled = false;
    $('#analysisNote').textContent = `${file.name}：中央框架已抽取。請把結果載入實驗台，進行重合成與相位對照。`;
    toast('WAV 分析完成');
  } catch (err) {
    $('#analysisState').textContent = '失敗'; $('#analysisState').className = 'status-badge';
    $('#analysisNote').textContent = err.message;
    toast(`分析失敗：${err.message}`);
  }
}

function analysisSpec() {
  const a = state.analysis;
  return {
    farhp_weblab_analysis_version: '0.1', file_name: a.fileName,
    analysis: { sample_rate_hz: a.sampleRate, frame_time_sec: a.frameStart, frame_length_sec: a.frameLength, f0_hz: a.f0, f0_confidence: a.confidence, applicability_grade: a.grade, method: 'browser_autocorrelation_harmonic_projection' },
    anchor: { type: 'fundamental', phase_rad: a.anchor, confidence: a.confidence },
    harmonics: { indices: a.amplitudes.map((_, i) => i + 1), amplitude: a.amplitudes, raw_amplitude: a.rawAmplitudes, absolute_phase_rad: a.phases, mask: a.mask.map(Number) },
    phase: { representation: 'angle_rad', harmonic_indices: a.farhp.slice(1).map((_, i) => i + 2), values: a.farhp.slice(1) },
    warning: 'single-frame MVP estimate; not glottal FARHP and not a physiological ground truth',
  };
}

function runShiftTest(showToast = true) {
  const dt = Number($('#shift').value) / 1000;
  const q = currentQuantizedPhase();
  let maxErr = 0;
  for (let i = 0; i < state.K; i++) {
    const k = i + 1;
    const phi = k * state.anchor + q[i];
    const shiftedPhi = phi - TAU * k * state.f0 * dt;
    const shiftedAnchor = state.anchor - TAU * state.f0 * dt;
    const recovered = i === 0 ? 0 : wrapPhase(shiftedPhi - k * shiftedAnchor);
    maxErr = Math.max(maxErr, circularDistance(recovered, q[i]));
  }
  const pass = maxErr < 1e-9;
  const el = $('#shiftResult'); el.className = `test-result ${pass ? 'pass' : 'fail'}`; el.textContent = `${pass ? 'PASS' : 'FAIL'}｜最大環距誤差 ${maxErr.toExponential(2)} rad`;
  if (showToast) toast(pass ? '時間平移不變性通過' : '時間平移不變性未通過');
}

function runQuantTest(showToast = true) {
  const m = quantMetrics();
  $('#quantRmse').textContent = `${fmt(m.rmse)} rad`; $('#quantMax').textContent = `${fmt(m.max)} rad`; $('#quantBound').textContent = state.quantM ? `${fmt(m.bound)} rad` : '0';
  const pass = !state.quantM || m.max <= m.bound + 1e-9;
  const el = $('#quantResult'); el.className = `test-result ${pass ? 'pass' : 'fail'}`; el.textContent = state.quantM ? `${pass ? 'PASS' : 'FAIL'}｜${state.quantM} 相量化符合 π/M 誤差界` : 'PASS｜目前使用連續相位，無量化誤差';
  if (showToast) toast('量化測試已更新');
}

function captureBaseline() {
  state.baseline = { f0: state.f0, duration: state.duration, anchor: state.anchor, amplitudes: state.amplitudes.slice(), phase: state.phase.slice() };
  const el = $('#invariantResult'); el.className = 'test-result pass'; el.textContent = '已捕捉基準。現在改變相位條件，再執行比較。';
  toast('FARHP-only 基準已建立');
}

function runInvariantTest() {
  if (!state.baseline) return captureBaseline();
  const b = state.baseline;
  const f0Same = Math.abs(b.f0 - state.f0) < 1e-9, durSame = Math.abs(b.duration - state.duration) < 1e-9, anchorSame = circularDistance(b.anchor, state.anchor) < 1e-9;
  const ampSame = b.amplitudes.length === state.amplitudes.length && b.amplitudes.every((v, i) => Math.abs(v - state.amplitudes[i]) < 1e-9);
  const phaseMove = b.phase.length === state.phase.length ? Math.sqrt(b.phase.slice(1).reduce((s, v, i) => s + circularDistance(v, state.phase[i + 1]) ** 2, 0) / Math.max(1, b.phase.length - 1)) : Infinity;
  const pass = f0Same && durSame && anchorSame && ampSame;
  const el = $('#invariantResult'); el.className = `test-result ${pass ? 'pass' : 'fail'}`;
  el.textContent = `${pass ? 'PASS' : 'FAIL'}｜f₀ ${f0Same ? '✓' : '✗'}・振幅 ${ampSame ? '✓' : '✗'}・時長 ${durSame ? '✓' : '✗'}・錨相位 ${anchorSame ? '✓' : '✗'}｜FARHP 位移 ${Number.isFinite(phaseMove) ? fmt(phaseMove) : '維度不同'} rad`;
}

const INITIALS = [
  { symbol: '', label: '∅／零聲母', type: 'none', groups: ['open','i','u','v'] },
  { symbol: 'ㄅ', label: 'ㄅ', type: 'stop_unasp', groups: ['open','i','u'] },
  { symbol: 'ㄆ', label: 'ㄆ', type: 'stop_asp', groups: ['open','i','u'] },
  { symbol: 'ㄇ', label: 'ㄇ', type: 'nasal', groups: ['open','i','u','v'] },
  { symbol: 'ㄈ', label: 'ㄈ', type: 'fricative', groups: ['open','u'] },
  { symbol: 'ㄉ', label: 'ㄉ', type: 'stop_unasp', groups: ['open','i','u'] },
  { symbol: 'ㄊ', label: 'ㄊ', type: 'stop_asp', groups: ['open','i','u'] },
  { symbol: 'ㄋ', label: 'ㄋ', type: 'nasal', groups: ['open','i','u','v'] },
  { symbol: 'ㄌ', label: 'ㄌ', type: 'lateral', groups: ['open','i','u','v'] },
  { symbol: 'ㄍ', label: 'ㄍ', type: 'stop_unasp', groups: ['open','u'] },
  { symbol: 'ㄎ', label: 'ㄎ', type: 'stop_asp', groups: ['open','u'] },
  { symbol: 'ㄏ', label: 'ㄏ', type: 'fricative', groups: ['open','u'] },
  { symbol: 'ㄐ', label: 'ㄐ', type: 'affricate_unasp', groups: ['i','v'] },
  { symbol: 'ㄑ', label: 'ㄑ', type: 'affricate_asp', groups: ['i','v'] },
  { symbol: 'ㄒ', label: 'ㄒ', type: 'fricative', groups: ['i','v'] },
  { symbol: 'ㄓ', label: 'ㄓ', type: 'affricate_unasp', groups: ['open','u','apical'] },
  { symbol: 'ㄔ', label: 'ㄔ', type: 'affricate_asp', groups: ['open','u','apical'] },
  { symbol: 'ㄕ', label: 'ㄕ', type: 'fricative', groups: ['open','u','apical'] },
  { symbol: 'ㄖ', label: 'ㄖ', type: 'approximant', groups: ['open','u','apical'] },
  { symbol: 'ㄗ', label: 'ㄗ', type: 'affricate_unasp', groups: ['open','u','apical'] },
  { symbol: 'ㄘ', label: 'ㄘ', type: 'affricate_asp', groups: ['open','u','apical'] },
  { symbol: 'ㄙ', label: 'ㄙ', type: 'fricative', groups: ['open','u','apical'] },
];

const FINALS = [
  { key:'a', symbol:'ㄚ', group:'open', sihu:'開口呼', path:['a'], coda:'無' },
  { key:'o', symbol:'ㄛ', group:'open', sihu:'開口呼', path:['o'], coda:'無' },
  { key:'e', symbol:'ㄜ', group:'open', sihu:'開口呼', path:['e'], coda:'無' },
  { key:'eh', symbol:'ㄝ', group:'open', sihu:'開口呼', path:['e'], coda:'無' },
  { key:'ai', symbol:'ㄞ', group:'open', sihu:'開口呼', path:['a','i'], coda:'無' },
  { key:'ei', symbol:'ㄟ', group:'open', sihu:'開口呼', path:['e','i'], coda:'無' },
  { key:'ao', symbol:'ㄠ', group:'open', sihu:'開口呼', path:['a','o'], coda:'無' },
  { key:'ou', symbol:'ㄡ', group:'open', sihu:'開口呼', path:['o','u'], coda:'無' },
  { key:'an', symbol:'ㄢ', group:'open', sihu:'開口呼', path:['a'], coda:'前鼻音 /n/' },
  { key:'en', symbol:'ㄣ', group:'open', sihu:'開口呼', path:['e'], coda:'前鼻音 /n/' },
  { key:'ang', symbol:'ㄤ', group:'open', sihu:'開口呼', path:['a'], coda:'後鼻音 /ŋ/' },
  { key:'eng', symbol:'ㄥ', group:'open', sihu:'開口呼', path:['e'], coda:'後鼻音 /ŋ/' },
  { key:'er', symbol:'ㄦ', group:'open', sihu:'開口呼', path:['er'], coda:'兒化／捲舌' },
  { key:'i', symbol:'ㄧ', group:'i', sihu:'齊齒呼', path:['i'], coda:'無' },
  { key:'ia', symbol:'ㄧㄚ', group:'i', sihu:'齊齒呼', path:['i','a'], coda:'無' },
  { key:'ie', symbol:'ㄧㄝ', group:'i', sihu:'齊齒呼', path:['i','e'], coda:'無' },
  { key:'iao', symbol:'ㄧㄠ', group:'i', sihu:'齊齒呼', path:['i','a','o'], coda:'無' },
  { key:'iou', symbol:'ㄧㄡ', group:'i', sihu:'齊齒呼', path:['i','o','u'], coda:'無' },
  { key:'ian', symbol:'ㄧㄢ', group:'i', sihu:'齊齒呼', path:['i','a'], coda:'前鼻音 /n/' },
  { key:'in', symbol:'ㄧㄣ', group:'i', sihu:'齊齒呼', path:['i'], coda:'前鼻音 /n/' },
  { key:'iang', symbol:'ㄧㄤ', group:'i', sihu:'齊齒呼', path:['i','a'], coda:'後鼻音 /ŋ/' },
  { key:'ing', symbol:'ㄧㄥ', group:'i', sihu:'齊齒呼', path:['i'], coda:'後鼻音 /ŋ/' },
  { key:'u', symbol:'ㄨ', group:'u', sihu:'合口呼', path:['u'], coda:'無' },
  { key:'ua', symbol:'ㄨㄚ', group:'u', sihu:'合口呼', path:['u','a'], coda:'無' },
  { key:'uo', symbol:'ㄨㄛ', group:'u', sihu:'合口呼', path:['u','o'], coda:'無' },
  { key:'uai', symbol:'ㄨㄞ', group:'u', sihu:'合口呼', path:['u','a','i'], coda:'無' },
  { key:'uei', symbol:'ㄨㄟ', group:'u', sihu:'合口呼', path:['u','e','i'], coda:'無' },
  { key:'uan', symbol:'ㄨㄢ', group:'u', sihu:'合口呼', path:['u','a'], coda:'前鼻音 /n/' },
  { key:'uen', symbol:'ㄨㄣ', group:'u', sihu:'合口呼', path:['u','e'], coda:'前鼻音 /n/' },
  { key:'uang', symbol:'ㄨㄤ', group:'u', sihu:'合口呼', path:['u','a'], coda:'後鼻音 /ŋ/' },
  { key:'ong', symbol:'ㄨㄥ', group:'u', sihu:'合口呼', path:['u','o'], coda:'後鼻音 /ŋ/' },
  { key:'v', symbol:'ㄩ', group:'v', sihu:'撮口呼', path:['y'], coda:'無' },
  { key:'ve', symbol:'ㄩㄝ', group:'v', sihu:'撮口呼', path:['y','e'], coda:'無' },
  { key:'van', symbol:'ㄩㄢ', group:'v', sihu:'撮口呼', path:['y','a'], coda:'前鼻音 /n/' },
  { key:'vn', symbol:'ㄩㄣ', group:'v', sihu:'撮口呼', path:['y'], coda:'前鼻音 /n/' },
  { key:'iong', symbol:'ㄩㄥ', group:'v', sihu:'撮口呼', path:['y','o'], coda:'後鼻音 /ŋ/' },
  { key:'apical', symbol:'', group:'apical', sihu:'舌尖元音', path:['apical'], coda:'無' },
];

const SYLLABLE_PRESETS = {
  ma1:{initial:'ㄇ', final:'a', tone:1}, ma2:{initial:'ㄇ', final:'a', tone:2},
  ma3:{initial:'ㄇ', final:'a', tone:3}, ma4:{initial:'ㄇ', final:'a', tone:4}, ma0:{initial:'ㄇ', final:'a', tone:0},
  xuan2:{initial:'ㄒ', final:'van', tone:2}, guang1:{initial:'ㄍ', final:'uang', tone:1},
  zhong1:{initial:'ㄓ', final:'ong', tone:1}, ren2:{initial:'ㄖ', final:'en', tone:2},
};

const TONE_NAMES = {0:'輕聲', 1:'第一聲', 2:'第二聲', 3:'第三聲', 4:'第四聲'};
const ONSET_NAMES = {
  none:'零聲母／平滑起音', stop_unasp:'不送氣塞音／爆破', stop_asp:'送氣塞音／爆破＋送氣',
  affricate_unasp:'不送氣塞擦音', affricate_asp:'送氣塞擦音', fricative:'擦音／高頻噪聲',
  nasal:'鼻音／預發聲', lateral:'邊音／平滑過渡', approximant:'近音／平滑過渡',
};

function initialInfo(symbol = syllableState.initial) { return INITIALS.find(x => x.symbol === symbol) ?? INITIALS[0]; }
function finalInfo(key = syllableState.final) { return FINALS.find(x => x.key === key) ?? FINALS[0]; }
function isSyllableCategoryAllowed(initialSymbol, finalKey) {
  const ini = initialInfo(initialSymbol), fin = finalInfo(finalKey);
  return ini.groups.includes(fin.group);
}
function toneMark(tone) { return tone === 2 ? 'ˊ' : tone === 3 ? 'ˇ' : tone === 4 ? 'ˋ' : ''; }
function bopomofoSyllable(initialSymbol, finalKey, tone) {
  const core = `${initialSymbol}${finalInfo(finalKey).symbol}`;
  return tone === 0 ? `˙${core}` : `${core}${toneMark(tone)}`;
}
function neutralToneSemitones(previousTone, u) {
  // Contextual neutral-tone targets are deliberately coarse MVP categories.
  const targets = {1:-3.2, 2:-0.7, 3:2.1, 4:-5.0, 0:-2.0};
  const target = targets[previousTone] ?? -2.0;
  return target + 0.8 * (1-u) - 0.35 * u;
}
function toneSemitones(tone, u, previousTone = null) {
  u = clamp(u, 0, 1);
  if (tone === 1) return 4.2 + 0.12 * Math.sin(Math.PI * u);
  if (tone === 2) return -1.6 + 7.1 * Math.pow(u, 1.18);
  if (tone === 3) {
    if (u < 0.56) return -1.0 - 5.0 * Math.pow(u / 0.56, 0.9);
    return -6.0 + 6.4 * Math.pow((u - 0.56) / 0.44, 1.12);
  }
  if (tone === 4) return 5.2 - 9.4 * Math.pow(u, 0.82);
  return previousTone == null ? -0.5 - 2.2 * u : neutralToneSemitones(previousTone, u);
}
function toneF0(tone, u, baseF0 = syllableState.baseF0, previousTone = null, prosodyStartSemi = 0, prosodyEndSemi = 0) {
  const prosody = prosodyStartSemi + (prosodyEndSemi - prosodyStartSemi) * smooth01(clamp(u,0,1));
  return baseF0 * Math.pow(2, (toneSemitones(tone, u, previousTone) + prosody) / 12);
}
function smooth01(x) { x = clamp(x,0,1); return x*x*(3-2*x); }
function vowelWeights(path, u) {
  if (path.length === 1) return [[path[0],1]];
  const x = smooth01(clamp(u,0,1));
  if (path.length === 2) return [[path[0],1-x],[path[1],x]];
  if (x < .5) { const a=smooth01(x*2); return [[path[0],1-a],[path[1],a]]; }
  const a=smooth01((x-.5)*2); return [[path[1],1-a],[path[2],a]];
}
function dynamicHarmonicAmplitude(fin, k, f0, u) {
  const freq = k * f0;
  let env = 0;
  for (const [key,w] of vowelWeights(fin.path, Math.min(u/.78,1))) env += w * formantEnvelope(freq, FORMANTS[key]);
  const strength = clamp(syllableState.formantCoarticulationStrength || 0, 0, 1);
  if (strength > 0 && syllableState.leftContextVowel && FORMANTS[syllableState.leftContextVowel]) {
    const mix = strength * (1 - smooth01(u / .17));
    env = env * (1 - mix) + formantEnvelope(freq, FORMANTS[syllableState.leftContextVowel]) * mix;
  }
  if (strength > 0 && syllableState.rightContextVowel && FORMANTS[syllableState.rightContextVowel]) {
    const mix = strength * smooth01((u - .81) / .19);
    env = env * (1 - mix) + formantEnvelope(freq, FORMANTS[syllableState.rightContextVowel]) * mix;
  }
  let amp = env / Math.pow(k, .86);
  const codaMix = smooth01((u - .70) / .27);
  if (fin.coda.includes('/n/')) amp *= (1 - .34*codaMix*(k/Math.max(8,state.K))) * (1 + .30*codaMix*Math.exp(-.5*((freq-260)/230)**2));
  if (fin.coda.includes('/ŋ/')) amp *= (1 - .42*codaMix*(k/Math.max(8,state.K))) * (1 + .38*codaMix*Math.exp(-.5*((freq-320)/260)**2));
  if (fin.coda.includes('兒化')) amp *= 1 + .30*codaMix*Math.exp(-.5*((freq-1550)/440)**2);
  return amp;
}
function onsetDuration(type) {
  return ({none:0, nasal:.055, lateral:.050, approximant:.055, stop_unasp:.060, stop_asp:.105, affricate_unasp:.090, affricate_asp:.125, fricative:.115})[type] ?? .06;
}
function syllablePhaseVector(K) {
  const src = syllableState.phaseSource;
  if (src === 'lab') {
    const q = currentQuantizedPhase();
    return Array.from({length:K}, (_,i) => i === 0 ? 0 : (q[i] ?? q[q.length-1] ?? 0));
  }
  return phasePreset(src, K);
}
function effectiveSyllableDuration() { return syllableState.tone === 0 ? Math.min(syllableState.duration * .68, .52) : syllableState.duration; }

function synthesizeSyllable() {
  const ini = initialInfo(), fin = finalInfo();
  const duration = effectiveSyllableDuration();
  const count = Math.max(1, Math.round(duration * SAMPLE_RATE));
  const out = new Float32Array(count);
  const K = Math.min(Math.max(12, state.K), 32);
  const targetPsi = syllablePhaseVector(K);
  const onsetSec = Math.min(onsetDuration(ini.type), duration*.28);
  const rng = mulberry32(syllableState.randomSeed + syllableState.tone * 97 + (ini.symbol.charCodeAt(0) || 0));
  let theta = 0, previousNoise = 0, peak = 0;
  const f0Track = new Float32Array(count);
  for (let n=0; n<count; n++) {
    const t=n/SAMPLE_RATE, u=t/duration;
    const voicedU=clamp((t-onsetSec)/(Math.max(duration-onsetSec,1e-5)),0,1);
    const contourU=ini.type === 'none' || ['nasal','lateral','approximant'].includes(ini.type) ? u : voicedU;
    const f0=toneF0(syllableState.tone, contourU, syllableState.baseF0, syllableState.contextPrevTone, syllableState.prosodyStartSemi, syllableState.prosodyEndSemi);
    f0Track[n]=f0; theta += TAU*f0/SAMPLE_RATE;
    const stopLike=['stop_unasp','stop_asp','affricate_unasp','affricate_asp','fricative'].includes(ini.type);
    const attack = stopLike ? smooth01((t-onsetSec*.72)/.035) : smooth01(t/.035);
    const release = smooth01((duration-t)/.045);
    const toneIntensity = syllableState.tone === 3 ? 1-.13*Math.exp(-.5*((contourU-.56)/.18)**2) : 1;
    const phaseRamp = smooth01((t-onsetSec*.45)/Math.max(.12,duration*.27));
    let voiced=0;
    for (let i=0; i<K; i++) {
      const k=i+1;
      if (k*f0>=SAMPLE_RATE/2) break;
      let amp=dynamicHarmonicAmplitude(fin,k,f0,voicedU);
      if (ini.type==='nasal' && t<onsetSec+.035) amp *= k<=4 ? .55 : .16;
      if (ini.type==='lateral' && t<onsetSec+.025) amp *= .42+.42*Math.exp(-k/5);
      const psi=i===0 ? 0 : geodesicInterpolate(0,targetPsi[i],syllableState.phaseStrength*phaseRamp);
      voiced += amp*Math.cos(k*theta+k*state.anchor+psi);
    }
    voiced *= attack*release*toneIntensity;
    const white=rng()*2-1, hp=white-previousNoise; previousNoise=white;
    let residual=0;
    if (ini.type==='stop_unasp' || ini.type==='stop_asp') {
      const center=onsetSec*.48, width=.0045;
      residual += hp*Math.exp(-.5*((t-center)/width)**2)*.95;
    }
    if (ini.type==='stop_asp') residual += hp*.34*smooth01((t-onsetSec*.35)/.012)*(1-smooth01((t-onsetSec)/.040));
    if (ini.type==='affricate_unasp' || ini.type==='affricate_asp') {
      const center=onsetSec*.28;
      residual += hp*Math.exp(-.5*((t-center)/.005)**2)*.75;
      residual += hp*.30*smooth01((t-center)/.008)*(1-smooth01((t-onsetSec)/.028));
    }
    if (ini.type==='affricate_asp') residual += hp*.24*smooth01((t-onsetSec*.35)/.010)*(1-smooth01((t-onsetSec)/.052));
    if (ini.type==='fricative') residual += hp*.33*(1-smooth01((t-onsetSec)/.030))*smooth01(t/.012);
    const codaMix=smooth01((u-.76)/.20);
    if (fin.coda.includes('/n/')) residual += .055*codaMix*Math.sin(TAU*245*t+state.anchor);
    if (fin.coda.includes('/ŋ/')) residual += .070*codaMix*Math.sin(TAU*310*t+state.anchor*.7);
    out[n]=voiced+syllableState.residualStrength*residual;
    peak=Math.max(peak,Math.abs(out[n]));
  }
  const scale=peak>1e-9 ? state.gain/peak : 1;
  for (let n=0;n<count;n++) out[n]*=scale;
  const f0Min=Math.min(...f0Track), f0Max=Math.max(...f0Track);
  syllableState.audio=out;
  syllableState.lastMeta={duration,K,onsetSec,f0Track,f0Min,f0Max,rawPeak:peak,initial:ini,final:fin,targetPsi};
  return {samples:out,...syllableState.lastMeta};
}

async function playSyllable() {
  stopAudio();
  const {samples}=synthesizeSyllable();
  state.audioCtx ??= new (window.AudioContext || window.webkitAudioContext)({sampleRate:SAMPLE_RATE});
  if (state.audioCtx.state==='suspended') await state.audioCtx.resume();
  const buffer=state.audioCtx.createBuffer(1,samples.length,SAMPLE_RATE); buffer.copyToChannel(samples,0);
  const source=state.audioCtx.createBufferSource(); source.buffer=buffer; source.connect(state.audioCtx.destination);
  source.onended=()=>{if(state.source===source)state.source=null;}; source.start(); state.source=source;
}
function syllableManifest() {
  const meta=syllableState.lastMeta ?? synthesizeSyllable();
  const ini=initialInfo(), fin=finalInfo();
  const points=Array.from({length:17},(_,i)=>({u:i/16,semitones:toneSemitones(syllableState.tone,i/16,syllableState.contextPrevTone)+(syllableState.prosodyStartSemi+(syllableState.prosodyEndSemi-syllableState.prosodyStartSemi)*smooth01(i/16)),f0_hz:toneF0(syllableState.tone,i/16,syllableState.baseF0,syllableState.contextPrevTone,syllableState.prosodyStartSemi,syllableState.prosodyEndSemi)}));
  return {
    farhp_weblab_syllable_version:'0.6', generated_at:new Date().toISOString(),
    phonology:{bopomofo:bopomofoSyllable(ini.symbol,fin.key,syllableState.tone),initial:ini.symbol||null,final:fin.symbol,tone:syllableState.tone,tone_name:TONE_NAMES[syllableState.tone],sihu:fin.sihu,coda:fin.coda,category_check:isSyllableCategoryAllowed(ini.symbol,fin.key)},
    acoustics:{sample_rate_hz:SAMPLE_RATE,duration_sec:meta.duration,base_f0_hz:syllableState.baseF0,f0_min_hz:meta.f0Min,f0_max_hz:meta.f0Max,onset_model:ini.type,residual_strength:syllableState.residualStrength,tone_trajectory:points},
    farhp:{source:syllableState.phaseSource,strength:syllableState.phaseStrength,anchor_phase_rad:state.anchor,harmonic_count:meta.K,quantization_bins:state.quantM,values:meta.targetPsi.slice(1)},
    decomposition:'phonology + f0(t) tone + FARHP + onset/coda residual',
    warning:'browser MVP synthesis; not a natural-speech TTS or physiological model',
  };
}

function drawToneContour() {
  const {ctx,w,h}=setupCanvas($('#toneCanvas')), p=palette(); drawGrid(ctx,w,h,p);
  const pad={l:48,r:18,t:18,b:32}, W=w-pad.l-pad.r,H=h-pad.t-pad.b;
  const values=Array.from({length:181},(_,i)=>toneF0(syllableState.tone,i/180,syllableState.baseF0,syllableState.contextPrevTone,syllableState.prosodyStartSemi,syllableState.prosodyEndSemi));
  const min=Math.min(...values)*.92,max=Math.max(...values)*1.08;
  ctx.strokeStyle=p.accent2; ctx.lineWidth=3; ctx.beginPath();
  values.forEach((v,i)=>{const x=pad.l+i/(values.length-1)*W,y=pad.t+(max-v)/(max-min)*H;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
  ctx.fillStyle=p.muted;ctx.font='12px sans-serif';ctx.fillText(`${fmt(max,0)} Hz`,5,pad.t+5);ctx.fillText(`${fmt(min,0)} Hz`,5,pad.t+H);ctx.fillText('音節時間 →',w-82,h-8);
}
function drawSyllableWave() {
  const {ctx,w,h}=setupCanvas($('#syllableWaveCanvas')),p=palette();drawGrid(ctx,w,h,p);
  const {samples,rawPeak}=synthesizeSyllable();
  const step=Math.max(1,Math.floor(samples.length/Math.max(1,w*2)));
  ctx.strokeStyle=p.accent;ctx.lineWidth=1.6;ctx.beginPath();
  for(let i=0;i<samples.length;i+=step){const x=i/(samples.length-1)*w,y=h/2-samples[i]/Math.max(state.gain,1e-6)*h*.42;i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();
  $('#syllablePeak').textContent=`Raw peak ${fmt(rawPeak,2)}`;
}
function updateFinalOptions() {
  const ini=initialInfo();
  for (const option of $('#finalSelect').options) option.disabled=!ini.groups.includes(option.dataset.group);
  if (!isSyllableCategoryAllowed(syllableState.initial,syllableState.final)) {
    const next=FINALS.find(f=>ini.groups.includes(f.group)); syllableState.final=next.key; $('#finalSelect').value=next.key;
  }
}
function syncSyllableControls() {
  $('#initialSelect').value=syllableState.initial; updateFinalOptions(); $('#finalSelect').value=syllableState.final;
  $('#syllableF0').value=syllableState.baseF0; $('#syllableDuration').value=syllableState.duration;
  $('#residualStrength').value=syllableState.residualStrength; $('#syllablePhaseStrength').value=syllableState.phaseStrength; $('#syllablePhaseSource').value=syllableState.phaseSource;
  $$('#toneButtons button').forEach(b=>b.classList.toggle('active',Number(b.dataset.tone)===syllableState.tone));
}
function updateSyllableUI() {
  const ini=initialInfo(),fin=finalInfo(),allowed=isSyllableCategoryAllowed(ini.symbol,fin.key);
  const text=bopomofoSyllable(ini.symbol,fin.key,syllableState.tone),meta=synthesizeSyllable();
  $('#syllableDisplay').textContent=text;$('#summaryBopomofo').textContent=text;
  $('#syllableStructure').textContent=`${ini.symbol||'零聲母'} + ${fin.symbol||'舌尖元音'} · ${TONE_NAMES[syllableState.tone]}`;
  $('#summaryFormula').textContent=`聲調 T${syllableState.tone}(t) × 韻母 ${fin.symbol||'舌尖元音'} × FARHP × ${ONSET_NAMES[ini.type]}`;
  $('#syllableF0Out').value=`${fmt(syllableState.baseF0,0)} Hz`;$('#syllableDurationOut').value=`${fmt(effectiveSyllableDuration(),2)} s`;
  $('#residualOut').value=`${Math.round(syllableState.residualStrength*100)}%`;$('#syllablePhaseOut').value=`${Math.round(syllableState.phaseStrength*100)}%`;
  $('#metricSihu').textContent=fin.sihu;$('#metricOnset').textContent=ONSET_NAMES[ini.type];$('#metricCoda').textContent=fin.coda;$('#metricF0Range').textContent=`${fmt(meta.f0Min,1)}–${fmt(meta.f0Max,1)} Hz`;
  $('#toneBadge').textContent=TONE_NAMES[syllableState.tone];
  $('#phonotacticState').className=`test-result ${allowed?'pass':'fail'}`;$('#phonotacticState').textContent=allowed?'結構檢查：音系類別可合成':'結構檢查：此聲母與四呼類別不相容';
  $('#layerPhonology').textContent=`${ini.symbol||'∅'}＋${fin.symbol||'舌尖元音'}`;$('#layerTone').textContent=`T${syllableState.tone}(t)`;$('#layerPhase').textContent=`${meta.K} 諧波／${syllableState.phaseSource}`;$('#layerResidual').textContent=ONSET_NAMES[ini.type];
  $('#syllableCertificate').textContent=`分層通過：FARHP 強度 ${fmt(syllableState.phaseStrength,2)} 只改變相對諧波相位；${TONE_NAMES[syllableState.tone]}仍由 ${fmt(meta.f0Min,1)}–${fmt(meta.f0Max,1)} Hz 的 f₀(t) 軌跡控制。`;
  drawToneContour();drawSyllableWave();
}
function applySyllablePreset(key) {
  const p=SYLLABLE_PRESETS[key];if(!p)return;
  syllableState.initial=p.initial;syllableState.final=p.final;syllableState.tone=p.tone;
  syncSyllableControls();updateSyllableUI();
}
function initSyllableComposer() {
  const initialSelect=$('#initialSelect'),finalSelect=$('#finalSelect');
  for(const ini of INITIALS){const o=document.createElement('option');o.value=ini.symbol;o.textContent=ini.label;initialSelect.appendChild(o);}
  for(const fin of FINALS){const o=document.createElement('option');o.value=fin.key;o.dataset.group=fin.group;o.textContent=fin.key==='apical'?'舌尖元音（聲母單獨成音節）':`${fin.symbol}｜${fin.sihu}`;finalSelect.appendChild(o);}
  syncSyllableControls();
  $('#syllablePreset').addEventListener('change',e=>{if(e.target.value!=='custom')applySyllablePreset(e.target.value);});
  initialSelect.addEventListener('change',e=>{syllableState.initial=e.target.value;$('#syllablePreset').value='custom';updateFinalOptions();syllableState.final=finalSelect.value;updateSyllableUI();});
  finalSelect.addEventListener('change',e=>{syllableState.final=e.target.value;$('#syllablePreset').value='custom';updateSyllableUI();});
  $$('#toneButtons button').forEach(b=>b.addEventListener('click',()=>{syllableState.tone=Number(b.dataset.tone);$('#syllablePreset').value='custom';syncSyllableControls();updateSyllableUI();}));
  $('#syllableF0').addEventListener('input',e=>{syllableState.baseF0=Number(e.target.value);updateSyllableUI();});
  $('#syllableDuration').addEventListener('input',e=>{syllableState.duration=Number(e.target.value);updateSyllableUI();});
  $('#residualStrength').addEventListener('input',e=>{syllableState.residualStrength=Number(e.target.value);updateSyllableUI();});
  $('#syllablePhaseStrength').addEventListener('input',e=>{syllableState.phaseStrength=Number(e.target.value);updateSyllableUI();});
  $('#syllablePhaseSource').addEventListener('change',e=>{syllableState.phaseSource=e.target.value;updateSyllableUI();});
  $('#playSyllableBtn').addEventListener('click',playSyllable);$('#heroSyllablePlay').addEventListener('click',playSyllable);$('#stopSyllableBtn').addEventListener('click',stopAudio);
  $('#syllableWavBtn').addEventListener('click',()=>objectUrlDownload(encodeWav(synthesizeSyllable().samples,SAMPLE_RATE),`farhp_${bopomofoSyllable(syllableState.initial,syllableState.final,syllableState.tone)}.wav`));
  $('#syllableJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(syllableManifest(),null,2)],{type:'application/json'}),'farhp_mandarin_syllable.json'));
  $('#sendToLabBtn').addEventListener('click',()=>{const fin=finalInfo();const key=fin.path[fin.path.length-1];state.vowel=FORMANTS[key]?key:'flat';state.f0=syllableState.baseF0;state.duration=effectiveSyllableDuration();state.phasePreset=syllableState.phaseSource==='lab'?'custom':syllableState.phaseSource;syncControls();rebuildModel({preserveCustom:syllableState.phaseSource==='lab'});location.hash='#lab';toast('音節核心已送入相位實驗台');});
  updateSyllableUI();
}


const UTTERANCE_PRESETS = {
  nihao: [
    {character:'你', initial:'ㄋ', final:'i', tone:3},
    {character:'好', initial:'ㄏ', final:'ao', tone:3},
  ],
  nihaoma: [
    {character:'你', initial:'ㄋ', final:'i', tone:3},
    {character:'好', initial:'ㄏ', final:'ao', tone:3},
    {character:'嗎', initial:'ㄇ', final:'a', tone:0},
  ],
  wohenhao: [
    {character:'我', initial:'', final:'uo', tone:3},
    {character:'很', initial:'ㄏ', final:'en', tone:3},
    {character:'好', initial:'ㄏ', final:'ao', tone:3},
  ],
  mamahao: [
    {character:'媽', initial:'ㄇ', final:'a', tone:1},
    {character:'媽', initial:'ㄇ', final:'a', tone:0},
    {character:'好', initial:'ㄏ', final:'ao', tone:3},
  ],
  yigebuhaoma: [
    {character:'一', initial:'', final:'i', tone:1},
    {character:'個', initial:'ㄍ', final:'e', tone:4},
    {character:'不', initial:'ㄅ', final:'u', tone:4},
    {character:'好', initial:'ㄏ', final:'ao', tone:3},
    {character:'嗎', initial:'ㄇ', final:'a', tone:0},
  ],
  yitianbuqu: [
    {character:'一', initial:'', final:'i', tone:1},
    {character:'天', initial:'ㄊ', final:'ian', tone:1},
    {character:'不', initial:'ㄅ', final:'u', tone:4},
    {character:'去', initial:'ㄑ', final:'v', tone:4},
  ],
  grouped: [
    {character:'我', initial:'', final:'uo', tone:3},
    {character:'很', initial:'ㄏ', final:'en', tone:3},
    {character:'好', initial:'ㄏ', final:'ao', tone:3, boundaryAfter:true},
    {character:'你', initial:'ㄋ', final:'i', tone:3},
    {character:'呢', initial:'ㄋ', final:'e', tone:0},
  ],
};
const UTTERANCE_PRESET_META = {
  nihao:{sentenceType:'declarative'}, nihaoma:{sentenceType:'question'}, wohenhao:{sentenceType:'declarative'},
  mamahao:{sentenceType:'declarative'}, yigebuhaoma:{sentenceType:'question'}, yitianbuqu:{sentenceType:'declarative'}, grouped:{sentenceType:'question'},
};

function currentSyllableConfig(character = '') {
  return {
    character,
    initial: syllableState.initial,
    final: syllableState.final,
    tone: syllableState.tone,
    baseF0: syllableState.baseF0,
    duration: syllableState.duration,
    residualStrength: syllableState.residualStrength,
    phaseStrength: syllableState.phaseStrength,
    phaseSource: syllableState.phaseSource,
    boundaryAfter: false,
  };
}
function normalizeUtteranceItem(item) {
  return {
    character:item.character ?? '', initial:item.initial ?? '', final:item.final ?? 'a', tone:Number(item.tone ?? 1),
    baseF0:Number(item.baseF0 ?? syllableState.baseF0), duration:Number(item.duration ?? syllableState.duration),
    residualStrength:Number(item.residualStrength ?? syllableState.residualStrength),
    phaseStrength:Number(item.phaseStrength ?? syllableState.phaseStrength), phaseSource:item.phaseSource ?? syllableState.phaseSource,
    boundaryAfter:Boolean(item.boundaryAfter),
  };
}
function applyUtterancePreset(key) {
  const preset=UTTERANCE_PRESETS[key]; if(!preset)return;
  utteranceState.preset=key;
  utteranceState.items=preset.map(normalizeUtteranceItem);
  utteranceState.sentenceType=UTTERANCE_PRESET_META[key]?.sentenceType ?? utteranceState.sentenceType;
  updateUtteranceUI();
}
function assignProsodicGroups(realized) {
  let group=0;
  realized.forEach((item,i)=>{
    item.prosodicGroup=group;
    if(utteranceState.prosodicGrouping && item.boundaryAfter && i<realized.length-1) group++;
  });
}
function sameProsodicGroup(a,b) { return !utteranceState.prosodicGrouping || a.prosodicGroup===b.prosodicGroup; }
function applyYiBuSandhi(realized) {
  if(!utteranceState.yiBuSandhi)return;
  for(let i=0;i<realized.length;i++) {
    const item=realized[i], next=realized[i+1];
    if(!next || !sameProsodicGroup(item,next)) continue;
    if(item.character==='一' && item.lexicalTone===1) {
      const target=next.surfaceTone===4?2:([1,2,3].includes(next.surfaceTone)?4:1);
      if(target!==item.surfaceTone) { item.surfaceTone=target; item.sandhiApplied=true; item.yiBuSandhiApplied=true; item.sandhiTypes.push('一變調'); }
    }
    if(item.character==='不' && item.lexicalTone===4 && next.surfaceTone===4) {
      item.surfaceTone=2; item.sandhiApplied=true; item.yiBuSandhiApplied=true; item.sandhiTypes.push('不變調');
    }
  }
}
function sentenceIntonationFor(item,index,n) {
  const strength=utteranceState.intonationStrength;
  if(utteranceState.sentenceType==='question') {
    if(index===n-1) return {start:.4*strength,end:4.8*strength};
    if(index===n-2) return {start:0,end:.7*strength};
  }
  if(utteranceState.sentenceType==='exclamation' && index===n-1) return {start:1.8*strength,end:-2.8*strength};
  if(utteranceState.sentenceType==='declarative' && index===n-1) return {start:0,end:-.7*strength};
  return {start:0,end:0};
}
function realizeUtterance(items = utteranceState.items) {
  const realized=items.map((item,index)=>({...normalizeUtteranceItem(item),index,lexicalTone:Number(item.tone),surfaceTone:Number(item.tone),sandhiApplied:false,thirdToneSandhiApplied:false,yiBuSandhiApplied:false,sandhiTypes:[]}));
  assignProsodicGroups(realized);
  if(utteranceState.sandhi) {
    for(let i=0;i<realized.length-1;i++) {
      if(sameProsodicGroup(realized[i],realized[i+1]) && realized[i].lexicalTone===3 && realized[i+1].lexicalTone===3) {
        realized[i].surfaceTone=2; realized[i].sandhiApplied=true; realized[i].thirdToneSandhiApplied=true; realized[i].sandhiTypes.push('三聲變調');
      }
    }
  }
  applyYiBuSandhi(realized);
  const groups=new Map();
  for(const item of realized){ if(!groups.has(item.prosodicGroup))groups.set(item.prosodicGroup,[]);groups.get(item.prosodicGroup).push(item); }
  realized.forEach((item,i)=>{
    const groupItems=groups.get(item.prosodicGroup), gi=groupItems.indexOf(item), gn=Math.max(1,groupItems.length);
    const declinationSemi=utteranceState.declination && gn>1 ? -1.8*gi/(gn-1) : 0;
    item.contextPrevTone=i && sameProsodicGroup(realized[i-1],item)?realized[i-1].surfaceTone:null;
    item.baseF0Realized=item.baseF0*Math.pow(2,declinationSemi/12);
    item.durationRealized=item.duration/utteranceState.speechRate;
    if(i===realized.length-1 || item.boundaryAfter) item.durationRealized*=1+utteranceState.finalLengthening;
    if(item.surfaceTone===0) item.durationRealized=Math.min(item.durationRealized*.68,.52/utteranceState.speechRate);
    item.contextualNeutral=Boolean(item.surfaceTone===0 && utteranceState.neutralContext && item.contextPrevTone!=null);
    if(!item.contextualNeutral) item.contextPrevTone=null;
    const intonation=sentenceIntonationFor(item,i,realized.length);
    item.prosodyStartSemi=intonation.start; item.prosodyEndSemi=intonation.end;
  });
  return realized;
}
function dominantVowel(finalKey, edge='right') {
  const fin=finalInfo(finalKey), path=fin.path;
  return edge==='left'?path[0]:path[path.length-1];
}
function synthesizeConfiguredSyllable(config) {
  const snapshot={...syllableState};
  Object.assign(syllableState,{
    initial:config.initial, final:config.final, tone:config.surfaceTone ?? config.tone,
    baseF0:config.baseF0Realized ?? config.baseF0, duration:config.durationRealized ?? config.duration,
    residualStrength:config.residualStrength, phaseStrength:config.phaseStrength, phaseSource:config.phaseSource,
    contextPrevTone:config.contextPrevTone ?? null,
    prosodyStartSemi:config.prosodyStartSemi ?? 0, prosodyEndSemi:config.prosodyEndSemi ?? 0,
    leftContextVowel:config.leftContextVowel ?? null, rightContextVowel:config.rightContextVowel ?? null,
    formantCoarticulationStrength:config.formantCoarticulationStrength ?? 0,
  });
  const result=synthesizeSyllable();
  const manifest=syllableManifest();
  Object.assign(syllableState,snapshot);
  return {...result,manifest};
}
function crossfadeAppend(left,leftF0,right,rightF0,overlap) {
  overlap=Math.max(0,Math.min(overlap,left.length-1,right.length-1));
  const out=new Float32Array(left.length+right.length-overlap);
  const f0=new Float32Array(out.length);
  out.set(left); f0.set(leftF0);
  const start=left.length-overlap;
  for(let j=0;j<overlap;j++) {
    const u=(j+1)/(overlap+1), a=Math.cos(u*Math.PI/2), b=Math.sin(u*Math.PI/2);
    out[start+j]=left[start+j]*a+right[j]*b;
    f0[start+j]=leftF0[start+j]*(1-u)+rightF0[j]*u;
  }
  out.set(right.subarray(overlap),left.length);
  f0.set(rightF0.subarray(overlap),left.length);
  return {samples:out,f0Track:f0,startSample:start};
}
function appendSilence(left,leftF0,silenceSamples) {
  if(silenceSamples<=0)return {samples:left,f0Track:leftF0,startSample:left.length};
  const out=new Float32Array(left.length+silenceSamples),f0=new Float32Array(out.length);
  out.set(left);f0.set(leftF0);
  return {samples:out,f0Track:f0,startSample:left.length+silenceSamples};
}
function synthesizeUtterance() {
  const realized=realizeUtterance();
  if(!realized.length) {
    const empty=new Float32Array(1); utteranceState.audio=empty;
    utteranceState.lastMeta={samples:empty,f0Track:empty,realized:[],boundaries:[],duration:0,rawPeak:0,groupBoundaries:[]};
    return utteranceState.lastMeta;
  }
  for(let i=0;i<realized.length;i++) {
    const leftConnected=i>0 && !(utteranceState.prosodicGrouping && realized[i-1].boundaryAfter);
    const rightConnected=i<realized.length-1 && !(utteranceState.prosodicGrouping && realized[i].boundaryAfter);
    realized[i].leftContextVowel=utteranceState.formantCoarticulation && leftConnected?dominantVowel(realized[i-1].final,'right'):null;
    realized[i].rightContextVowel=utteranceState.formantCoarticulation && rightConnected?dominantVowel(realized[i+1].final,'left'):null;
    realized[i].formantCoarticulationStrength=utteranceState.formantCoarticulation ? .62 : 0;
  }
  let output=null, f0Track=null;
  const boundaries=[], groupBoundaries=[];
  const syllables=[];
  const requestedOverlap=utteranceState.coarticulation?Math.round(utteranceState.overlapMs/1000*SAMPLE_RATE):0;
  const pauseSamples=Math.round(utteranceState.groupPauseMs/1000*SAMPLE_RATE);
  for(let i=0;i<realized.length;i++) {
    const item=realized[i], syn=synthesizeConfiguredSyllable(item);
    syllables.push({item,syn});
    if(output===null) {
      output=syn.samples.slice(); f0Track=syn.f0Track.slice();
      boundaries.push({index:i,start_sample:0,end_sample:output.length,overlap_samples:0,pause_before_samples:0});
    } else {
      const previous=realized[i-1], groupedBoundary=utteranceState.prosodicGrouping && previous.boundaryAfter;
      let pauseBefore=0;
      if(groupedBoundary) {
        const withPause=appendSilence(output,f0Track,pauseSamples);output=withPause.samples;f0Track=withPause.f0Track;pauseBefore=pauseSamples;
        groupBoundaries.push({after_index:i-1,pause_samples:pauseSamples,start_sample:output.length-pauseSamples,end_sample:output.length});
      }
      const overlap=groupedBoundary?0:requestedOverlap;
      const joined=crossfadeAppend(output,f0Track,syn.samples,syn.f0Track,overlap);
      const start=joined.startSample;
      output=joined.samples; f0Track=joined.f0Track;
      boundaries.push({index:i,start_sample:start,end_sample:output.length,overlap_samples:Math.min(overlap,syn.samples.length-1),pause_before_samples:pauseBefore});
    }
  }
  let rawPeak=0; for(const x of output) rawPeak=Math.max(rawPeak,Math.abs(x));
  const scale=rawPeak>state.gain&&rawPeak>1e-9?state.gain/rawPeak:1;
  if(scale!==1) for(let i=0;i<output.length;i++) output[i]*=scale;
  const positive=Array.from(f0Track).filter(v=>v>0);
  const meta={samples:output,f0Track,realized,boundaries,groupBoundaries,syllables,duration:output.length/SAMPLE_RATE,rawPeak,f0Min:positive.length?Math.min(...positive):0,f0Max:positive.length?Math.max(...positive):0};
  utteranceState.audio=output; utteranceState.lastMeta=meta; return meta;
}
function surfaceBopomofo(item) { return bopomofoSyllable(item.initial,item.final,item.surfaceTone); }
function lexicalBopomofo(item) { return bopomofoSyllable(item.initial,item.final,item.lexicalTone ?? item.tone); }
function utteranceManifest() {
  const meta=utteranceState.lastMeta ?? synthesizeUtterance();
  return {
    farhp_weblab_utterance_version:'0.6', generated_at:new Date().toISOString(), sample_rate_hz:SAMPLE_RATE,
    text:meta.realized.map(x=>x.character).join(''),
    sentence_type:utteranceState.sentenceType,
    lexical_bopomofo:meta.realized.map(lexicalBopomofo), surface_bopomofo:meta.realized.map(surfaceBopomofo),
    rules:{
      third_tone_sandhi:utteranceState.sandhi, yi_bu_sandhi:utteranceState.yiBuSandhi,
      neutral_tone_context:utteranceState.neutralContext, prosodic_grouping:utteranceState.prosodicGrouping,
      coarticulation_crossfade:utteranceState.coarticulation, formant_parameter_interpolation:utteranceState.formantCoarticulation,
      phrase_declination:utteranceState.declination, sentence_intonation:utteranceState.sentenceType,
      intonation_strength:utteranceState.intonationStrength, speech_rate:utteranceState.speechRate,
      boundary_overlap_ms:utteranceState.overlapMs, group_pause_ms:utteranceState.groupPauseMs, final_lengthening:utteranceState.finalLengthening,
    },
    prosodic_groups:meta.groupBoundaries,
    syllables:meta.realized.map((x,i)=>({
      index:i,character:x.character||null,initial:x.initial||null,final:x.final,lexical_tone:x.lexicalTone,surface_tone:x.surfaceTone,
      lexical_bopomofo:lexicalBopomofo(x),surface_bopomofo:surfaceBopomofo(x),sandhi_applied:x.sandhiApplied,
      sandhi_types:x.sandhiTypes,third_tone_sandhi:x.thirdToneSandhiApplied,yi_bu_sandhi:x.yiBuSandhiApplied,
      prosodic_group:x.prosodicGroup,boundary_after:x.boundaryAfter,contextual_neutral:x.contextualNeutral,
      previous_surface_tone:x.contextPrevTone,base_f0_hz:x.baseF0Realized,duration_sec:x.durationRealized,
      sentence_intonation_semitones:{start:x.prosodyStartSemi,end:x.prosodyEndSemi},
      vocal_tract_context:{left_vowel:x.leftContextVowel,right_vowel:x.rightContextVowel,interpolation_strength:x.formantCoarticulationStrength},
      farhp:{source:x.phaseSource,strength:x.phaseStrength},boundary:meta.boundaries[i],
    })),
    acoustics:{duration_sec:meta.duration,f0_min_hz:meta.f0Min,f0_max_hz:meta.f0Max,raw_peak:meta.rawPeak},
    decomposition:'lexical phonology -> prosodic grouping -> tone sandhi -> contextual neutral tone -> phrase/sentence intonation -> vocal-tract interpolation -> syllable FARHP -> boundary rendering',
    warning:'MVP prosody and formant-interpolation model; not a natural-speech TTS or full syntactic/physiological parser',
  };
}
async function playUtterance() {
  stopAudio(); const {samples}=synthesizeUtterance(); if(samples.length<=1)return;
  state.audioCtx ??=new (window.AudioContext||window.webkitAudioContext)({sampleRate:SAMPLE_RATE});
  if(state.audioCtx.state==='suspended')await state.audioCtx.resume();
  const buffer=state.audioCtx.createBuffer(1,samples.length,SAMPLE_RATE);buffer.copyToChannel(samples,0);
  const source=state.audioCtx.createBufferSource();source.buffer=buffer;source.connect(state.audioCtx.destination);source.onended=()=>{if(state.source===source)state.source=null;};source.start();state.source=source;
}
function drawUtteranceF0() {
  const canvas=$('#utteranceF0Canvas'); if(!canvas)return;
  const {ctx,w,h}=setupCanvas(canvas),p=palette();drawGrid(ctx,w,h,p);const meta=utteranceState.lastMeta ?? synthesizeUtterance();
  if(meta.realized.length===0 || meta.f0Max<=0)return;
  const pad={l:48,r:18,t:18,b:32},W=w-pad.l-pad.r,H=h-pad.t-pad.b,min=meta.f0Min*.92,max=meta.f0Max*1.08;
  ctx.strokeStyle=p.accent2;ctx.lineWidth=2.5;ctx.beginPath();
  const step=Math.max(1,Math.floor(meta.f0Track.length/(w*2)));let drawing=false;
  for(let i=0;i<meta.f0Track.length;i+=step){
    const v=meta.f0Track[i];if(v<=0){drawing=false;continue;}
    const x=pad.l+i/(meta.f0Track.length-1)*W,y=pad.t+(max-v)/(max-min)*H;
    if(!drawing){ctx.moveTo(x,y);drawing=true;}else ctx.lineTo(x,y);
  }ctx.stroke();
  ctx.font='12px sans-serif';ctx.fillStyle=p.muted;
  for(const b of meta.boundaries){const x=pad.l+b.start_sample/(meta.f0Track.length-1)*W;ctx.strokeStyle=p.line;ctx.beginPath();ctx.moveTo(x,pad.t);ctx.lineTo(x,pad.t+H);ctx.stroke();const label=surfaceBopomofo(meta.realized[b.index]);ctx.fillStyle=p.muted;ctx.fillText(label,x+4,pad.t+14);}
  for(const g of meta.groupBoundaries){const x=pad.l+g.start_sample/(meta.f0Track.length-1)*W;ctx.strokeStyle=p.accent3;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,pad.t);ctx.lineTo(x,pad.t+H);ctx.stroke();ctx.fillStyle=p.accent3;ctx.fillText('｜',x+2,pad.t+H-4);}
  ctx.fillStyle=p.muted;ctx.fillText(`${fmt(max,0)} Hz`,4,pad.t+5);ctx.fillText(`${fmt(min,0)} Hz`,4,pad.t+H);
}
function drawUtteranceWave() {
  const canvas=$('#utteranceWaveCanvas');if(!canvas)return;
  const {ctx,w,h}=setupCanvas(canvas),p=palette();drawGrid(ctx,w,h,p);const meta=utteranceState.lastMeta ?? synthesizeUtterance();if(meta.samples.length<=1)return;
  const step=Math.max(1,Math.floor(meta.samples.length/(w*2)));ctx.strokeStyle=p.accent;ctx.lineWidth=1.4;ctx.beginPath();
  for(let i=0;i<meta.samples.length;i+=step){const x=i/(meta.samples.length-1)*w,y=h/2-meta.samples[i]/Math.max(state.gain,1e-6)*h*.42;i?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();
  $('#utterancePeakBadge').textContent=`Raw peak ${fmt(meta.rawPeak,2)}`;
}
function renderSequenceList(realized) {
  const host=$('#sequenceList'); if(!host)return; host.innerHTML='';
  realized.forEach((item,i)=>{
    const row=document.createElement('article');row.className=`sequence-item${item.boundaryAfter?' has-boundary':''}`;
    const ruleText=item.sandhiTypes.length?`${item.sandhiTypes.join('＋')} → `:'';
    const contextText=item.contextualNeutral?` · 前調 ${item.contextPrevTone} 後輕聲`:'';
    row.innerHTML=`<span class="sequence-index">${i+1}</span><div><b>${item.character||'自訂'} · ${lexicalBopomofo(item)}</b><small>${ruleText}${surfaceBopomofo(item)}${contextText} · 韻律組 ${item.prosodicGroup+1}</small></div><span class="phase-pill">${item.phaseSource}</span><button type="button" class="boundary-btn" data-boundary="${i}" aria-label="切換第 ${i+1} 音節後韻律邊界">${item.boundaryAfter?'｜':'·'}</button><button type="button" data-remove="${i}" aria-label="移除第 ${i+1} 音節">×</button>`;
    host.appendChild(row);
  });
  host.querySelectorAll('[data-remove]').forEach(btn=>btn.addEventListener('click',()=>{utteranceState.items.splice(Number(btn.dataset.remove),1);utteranceState.preset='custom';$('#utterancePreset').value='custom';updateUtteranceUI();}));
  host.querySelectorAll('[data-boundary]').forEach(btn=>btn.addEventListener('click',()=>{const i=Number(btn.dataset.boundary);utteranceState.items[i].boundaryAfter=!utteranceState.items[i].boundaryAfter;utteranceState.preset='custom';$('#utterancePreset').value='custom';updateUtteranceUI();}));
}
function updateUtteranceUI() {
  const meta=synthesizeUtterance(), realized=meta.realized;
  if($('#utterancePreset'))$('#utterancePreset').value=utteranceState.preset;
  $('#speechRate').value=utteranceState.speechRate;$('#boundaryOverlap').value=utteranceState.overlapMs;$('#groupPause').value=utteranceState.groupPauseMs;$('#finalLengthening').value=utteranceState.finalLengthening;$('#intonationStrength').value=utteranceState.intonationStrength;
  $('#sentenceType').value=utteranceState.sentenceType;
  $('#sandhiEnabled').checked=utteranceState.sandhi;$('#yiBuSandhiEnabled').checked=utteranceState.yiBuSandhi;$('#neutralContextEnabled').checked=utteranceState.neutralContext;$('#prosodicGroupingEnabled').checked=utteranceState.prosodicGrouping;$('#coarticulationEnabled').checked=utteranceState.coarticulation;$('#formantCoarticulationEnabled').checked=utteranceState.formantCoarticulation;$('#declinationEnabled').checked=utteranceState.declination;
  $('#speechRateOut').value=`${fmt(utteranceState.speechRate,2)}×`;$('#overlapOut').value=`${utteranceState.overlapMs} ms`;$('#groupPauseOut').value=`${utteranceState.groupPauseMs} ms`;$('#finalLengthOut').value=`${Math.round(utteranceState.finalLengthening*100)}%`;$('#intonationOut').value=`${Math.round(utteranceState.intonationStrength*100)}%`;
  const lexical=realized.map(lexicalBopomofo).join('　')||'尚未加入音節',surface=realized.map(surfaceBopomofo).join('　')||'—';
  $('#utteranceLexical').textContent=lexical;$('#utteranceSurface').textContent=surface;$('#utteranceDurationBadge').textContent=`${fmt(meta.duration,2)} s`;
  const third=realized.filter(x=>x.thirdToneSandhiApplied).length,yibu=realized.filter(x=>x.yiBuSandhiApplied).length,neutral=realized.filter(x=>x.contextualNeutral).length;
  const groups=realized.length?Math.max(...realized.map(x=>x.prosodicGroup))+1:0;
  $('#utteranceRuleCertificate').textContent=`規則證書：${third} 個三聲改寫；${yibu} 個一／不改寫；${neutral} 個語境輕聲；${groups} 個韻律組；${utteranceState.sentenceType} 句調；FARHP 仍逐音節保存。`;
  $('#utteranceF0Badge').textContent=realized.length?`${fmt(meta.f0Min,1)}–${fmt(meta.f0Max,1)} Hz`:'F₀ —';
  renderSequenceList(realized);drawUtteranceF0();drawUtteranceWave();
}
function initUtteranceComposer() {
  $('#utterancePreset').addEventListener('change',e=>{if(e.target.value!=='custom')applyUtterancePreset(e.target.value);else utteranceState.preset='custom';});
  $('#addCurrentSyllable').addEventListener('click',()=>{utteranceState.items.push(currentSyllableConfig());utteranceState.preset='custom';$('#utterancePreset').value='custom';updateUtteranceUI();toast('已加入目前音節');});
  $('#clearUtterance').addEventListener('click',()=>{utteranceState.items=[];utteranceState.preset='custom';$('#utterancePreset').value='custom';updateUtteranceUI();});
  const checks=[['#sandhiEnabled','sandhi'],['#yiBuSandhiEnabled','yiBuSandhi'],['#neutralContextEnabled','neutralContext'],['#prosodicGroupingEnabled','prosodicGrouping'],['#coarticulationEnabled','coarticulation'],['#formantCoarticulationEnabled','formantCoarticulation'],['#declinationEnabled','declination']];
  checks.forEach(([sel,key])=>$(sel).addEventListener('change',e=>{utteranceState[key]=e.target.checked;updateUtteranceUI();}));
  $('#sentenceType').addEventListener('change',e=>{utteranceState.sentenceType=e.target.value;updateUtteranceUI();});
  $('#speechRate').addEventListener('input',e=>{utteranceState.speechRate=Number(e.target.value);updateUtteranceUI();});
  $('#boundaryOverlap').addEventListener('input',e=>{utteranceState.overlapMs=Number(e.target.value);updateUtteranceUI();});
  $('#groupPause').addEventListener('input',e=>{utteranceState.groupPauseMs=Number(e.target.value);updateUtteranceUI();});
  $('#finalLengthening').addEventListener('input',e=>{utteranceState.finalLengthening=Number(e.target.value);updateUtteranceUI();});
  $('#intonationStrength').addEventListener('input',e=>{utteranceState.intonationStrength=Number(e.target.value);updateUtteranceUI();});
  $('#playUtteranceBtn').addEventListener('click',playUtterance);$('#stopUtteranceBtn').addEventListener('click',stopAudio);
  $('#utteranceWavBtn').addEventListener('click',()=>objectUrlDownload(encodeWav(synthesizeUtterance().samples,SAMPLE_RATE),'farhp_mandarin_utterance.wav'));
  $('#utteranceJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(utteranceManifest(),null,2)],{type:'application/json'}),'farhp_mandarin_utterance.json'));
  applyUtterancePreset('nihaoma');
}



function experimentPhaseSource(condition) {
  return condition === 'zero' ? 'aligned' : condition;
}

function cloneExperimentMeta(meta) {
  return {
    samples: meta.samples.slice(),
    f0Track: meta.f0Track.slice(),
    duration: meta.duration,
    f0Min: meta.f0Min,
    f0Max: meta.f0Max,
    rawPeak: meta.rawPeak,
    lexical: meta.realized.map(lexicalBopomofo),
    surface: meta.realized.map(surfaceBopomofo),
  };
}

function synthesizeUtteranceVariant(condition = 'identity', strength = 1, seed = 20260727) {
  const snapshot = {
    items: utteranceState.items,
    audio: utteranceState.audio,
    lastMeta: utteranceState.lastMeta,
    stateRandomSeed: state.randomSeed,
    syllableRandomSeed: syllableState.randomSeed,
  };
  try {
    utteranceState.items = snapshot.items.map(item => {
      const copy = {...item};
      if (condition !== 'identity') {
        copy.phaseSource = experimentPhaseSource(condition);
        copy.phaseStrength = strength;
      }
      return copy;
    });
    state.randomSeed = Number(seed) >>> 0;
    syllableState.randomSeed = (Number(seed) ^ 0x5f3759df) >>> 0;
    return cloneExperimentMeta(synthesizeUtterance());
  } finally {
    utteranceState.items = snapshot.items;
    utteranceState.audio = snapshot.audio;
    utteranceState.lastMeta = snapshot.lastMeta;
    state.randomSeed = snapshot.stateRandomSeed;
    syllableState.randomSeed = snapshot.syllableRandomSeed;
  }
}

function maxTrackDifference(a, b) {
  if (a.length !== b.length) return Infinity;
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
  return m;
}

function waveformRmsDifference(a, b) {
  if (a.length !== b.length || !a.length) return Infinity;
  let sum = 0;
  for (let i = 0; i < a.length; i++) sum += (a[i] - b[i]) ** 2;
  return Math.sqrt(sum / a.length);
}

function median(values) {
  if (!values.length) return null;
  const sorted = values.slice().sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function makeBalancedAbxTrials(count, seed) {
  const patterns = [
    {a_condition:'baseline', b_condition:'altered', x_condition:'baseline'},
    {a_condition:'baseline', b_condition:'altered', x_condition:'altered'},
    {a_condition:'altered', b_condition:'baseline', x_condition:'baseline'},
    {a_condition:'altered', b_condition:'baseline', x_condition:'altered'},
  ];
  const rng = mulberry32(Number(seed) >>> 0);
  const design = Array.from({length:count}, (_, i) => ({...patterns[i % patterns.length]}));
  for (let i = design.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [design[i], design[j]] = [design[j], design[i]];
  }
  return design.map((d, i) => ({
    trial:i + 1,
    ...d,
    correct_answer:d.x_condition === d.a_condition ? 'A' : 'B',
    play_counts:{A:0, B:0, X:0},
    started_at_ms:null,
    response:null,
  }));
}

function hashString32(text) {
  let h = 2166136261;
  for (const ch of String(text)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

function participantCode() {
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const rng = mulberry32((Date.now() ^ Math.floor(Math.random()*0xffffffff)) >>> 0);
  return `P-${Array.from({length:6},()=>alphabet[Math.floor(rng()*alphabet.length)]).join('')}`;
}

function latinStimulusOrder(keys, rowIndex = 0) {
  const n = keys.length;
  if (n <= 1) return keys.slice();
  const base = [];
  let lo = 0, hi = n - 1;
  while (lo <= hi) {
    base.push(lo++);
    if (lo <= hi) base.push(hi--);
  }
  const shift = ((rowIndex % n) + n) % n;
  return base.map(i => keys[(i + shift) % n]);
}

function selectedStimulusKeys() {
  const nodes = $$('#stimulusPool input[type="checkbox"]:checked');
  return nodes.map(x => x.value).filter(x => STUDY_STIMULUS_MAP[x]);
}

function withUtterancePreset(presetKey, callback) {
  const snap = {
    items: utteranceState.items, preset: utteranceState.preset, sentenceType: utteranceState.sentenceType,
    audio: utteranceState.audio, lastMeta: utteranceState.lastMeta,
  };
  try {
    utteranceState.items = UTTERANCE_PRESETS[presetKey].map(normalizeUtteranceItem);
    utteranceState.preset = presetKey;
    utteranceState.sentenceType = UTTERANCE_PRESET_META[presetKey]?.sentenceType ?? 'declarative';
    return callback();
  } finally {
    Object.assign(utteranceState, snap);
  }
}

function synthesizeStudyStimulus(presetKey, condition, strength, seed) {
  return withUtterancePreset(presetKey, () => {
    utteranceState.lastMeta = null;
    const sourceManifest = JSON.parse(JSON.stringify(utteranceManifest()));
    const audio = synthesizeUtteranceVariant(condition, strength, seed);
    return {sourceManifest, audio};
  });
}

function stimulusInvariantCertificate(baseline, altered) {
  const f0MaxDifference = maxTrackDifference(baseline.f0Track, altered.f0Track);
  const waveformRms = waveformRmsDifference(baseline.samples, altered.samples);
  const cert = {
    same_sample_count: baseline.samples.length === altered.samples.length,
    same_duration: Math.abs(baseline.duration - altered.duration) < 1e-12,
    max_f0_track_difference_hz: f0MaxDifference,
    same_lexical_bopomofo: JSON.stringify(baseline.lexical) === JSON.stringify(altered.lexical),
    same_surface_bopomofo: JSON.stringify(baseline.surface) === JSON.stringify(altered.surface),
    waveform_rms_difference: waveformRms,
  };
  cert.pass = cert.same_sample_count && cert.same_duration && cert.max_f0_track_difference_hz < 1e-9 && cert.same_lexical_bopomofo && cert.same_surface_bopomofo && waveformRms > 1e-7;
  return cert;
}

function buildStudyTrialPlan(stimulusKeys, repeats, practiceCount, participantId, seed) {
  const participantRow = hashString32(participantId) % Math.max(1, stimulusKeys.length);
  const ordered = [];
  for (let r=0; r<repeats; r++) ordered.push(...latinStimulusOrder(stimulusKeys, participantRow + r));
  const patterns = makeBalancedAbxTrials(ordered.length, seed + 7001);
  const main = ordered.map((stimulusKey, i) => ({...patterns[i], stimulus_key:stimulusKey, is_practice:false, main_ordinal:i+1}));
  const practicePatterns = makeBalancedAbxTrials(practiceCount, seed + 9001);
  const practice = practicePatterns.map((t,i)=>({...t, stimulus_key:stimulusKeys[i % stimulusKeys.length], is_practice:true, practice_ordinal:i+1}));
  const all = [...practice, ...main].map((t,i)=>({...t, sequence_index:i+1}));
  return {participantRow, orderedStimuli:ordered, trials:all};
}

function experimentSummary(session = experimentState.session) {
  if (!session) return {answered:0, correct:0, accuracy:null, medianRtMs:null, totalReplays:0, practiceAnswered:0, mainTotal:0};
  const main = session.trials.filter(t => !t.is_practice);
  const answeredTrials = main.filter(t => t.response);
  const correct = answeredTrials.filter(t => t.response.correct).length;
  const rts = answeredTrials.map(t => t.response.rt_ms);
  const totalReplays = session.trials.reduce((sum, t) => sum + Math.max(0, (t.play_counts?.A || 0) - 1) + Math.max(0, (t.play_counts?.B || 0) - 1) + Math.max(0, (t.play_counts?.X || 0) - 1), 0);
  return {
    answered: answeredTrials.length, correct, accuracy: answeredTrials.length ? correct / answeredTrials.length : null,
    medianRtMs: median(rts), totalReplays,
    practiceAnswered: session.trials.filter(t=>t.is_practice && t.response).length,
    mainTotal: main.length,
  };
}

function buildExperimentSession() {
  experimentState.condition = $('#experimentCondition').value;
  experimentState.strength = Number($('#experimentStrength').value);
  experimentState.repeats = Number($('#studyRepeats').value);
  experimentState.practiceCount = Number($('#practiceTrials').value);
  experimentState.breakEvery = Number($('#breakEvery').value);
  experimentState.seed = Math.max(1, Number($('#experimentSeed').value) || 20260731);
  experimentState.studyId = ($('#studyId').value || 'FARHP-PERCEPT-v0.6').trim();
  experimentState.participantId = ($('#participantId').value || participantCode()).trim();
  experimentState.selectedStimuli = selectedStimulusKeys();

  if (experimentState.selectedStimuli.length < 2) { toast('請至少選擇兩組刺激'); return null; }
  if (!experimentState.studyId || !experimentState.participantId) { toast('研究 ID 與匿名受試者 ID 不可為空'); return null; }

  const stimulusPool = {};
  const certificates = [];
  for (let i=0;i<experimentState.selectedStimuli.length;i++) {
    const key = experimentState.selectedStimuli[i];
    const baseSeed = (experimentState.seed + hashString32(key) + i*104729) >>> 0;
    const baselinePack = synthesizeStudyStimulus(key, 'identity', 1, baseSeed);
    const alteredPack = synthesizeStudyStimulus(key, experimentState.condition, experimentState.strength, baseSeed + 65537);
    const certificate = {stimulus_key:key, ...stimulusInvariantCertificate(baselinePack.audio, alteredPack.audio)};
    stimulusPool[key] = {
      key, label:STUDY_STIMULUS_MAP[key].label, bopomofo:STUDY_STIMULUS_MAP[key].bopomofo,
      source_manifest:baselinePack.sourceManifest,
      audio:{baseline:baselinePack.audio.samples, altered:alteredPack.audio.samples},
      invariant_certificate:certificate,
      duration_seconds:baselinePack.audio.duration,
    };
    certificates.push(certificate);
  }
  const plan = buildStudyTrialPlan(experimentState.selectedStimuli, experimentState.repeats, experimentState.practiceCount, experimentState.participantId, experimentState.seed);
  const allPass = certificates.every(x=>x.pass);
  experimentState.session = {
    session_id:`${experimentState.studyId}-${experimentState.participantId}-${experimentState.seed}-${Date.now()}`,
    study_id:experimentState.studyId, participant_id:experimentState.participantId,
    created_at:new Date().toISOString(), completed_at:null,
    task:'multi_stimulus_ABX_identity_match', seed:experimentState.seed,
    altered_condition:experimentState.condition, altered_condition_label:EXPERIMENT_CONDITION_LABELS[experimentState.condition],
    strength:experimentState.strength, repeats:experimentState.repeats,
    practice_count:experimentState.practiceCount, break_every:experimentState.breakEvery,
    selected_stimuli:experimentState.selectedStimuli.slice(), participant_latin_row:plan.participantRow,
    ordering_method: experimentState.selectedStimuli.length % 2 === 0 ? 'participant_indexed_mirrored_latin_row' : 'participant_indexed_cyclic_latin_row',
    stimulus_pool:stimulusPool, invariant_certificates:certificates, invariant_pass:allPass,
    trials:plan.trials, on_break:false, break_count:0,
  };
  experimentState.currentIndex = 0;
  updateExperimentUI();
  toast('多刺激研究已建立；正式輪條件映射已封存');
  return experimentState.session;
}

function currentExperimentTrial() { return experimentState.session?.trials?.[experimentState.currentIndex] ?? null; }

async function playFloatSamples(samples) {
  stopAudio();
  state.audioCtx ??= new (window.AudioContext || window.webkitAudioContext)({sampleRate:SAMPLE_RATE});
  if (state.audioCtx.state === 'suspended') await state.audioCtx.resume();
  const buffer = state.audioCtx.createBuffer(1, samples.length, SAMPLE_RATE);
  buffer.copyToChannel(samples, 0);
  const source = state.audioCtx.createBufferSource();
  source.buffer = buffer; source.connect(state.audioCtx.destination);
  source.onended = () => { if (state.source === source) state.source = null; };
  source.start(); state.source = source;
}

function samplesForExperimentLabel(label) {
  const session=experimentState.session, trial=currentExperimentTrial();
  if (!session || !trial) return null;
  const condition = label==='A' ? trial.a_condition : label==='B' ? trial.b_condition : trial.x_condition;
  return session.stimulus_pool[trial.stimulus_key]?.audio?.[condition] ?? null;
}

async function playExperimentStimulus(label) {
  const session=experimentState.session, trial=currentExperimentTrial();
  if (!trial || trial.response || session?.on_break) return;
  if (trial.started_at_ms == null) trial.started_at_ms = Date.now();
  trial.play_counts[label]++; updateExperimentUI();
  const samples=samplesForExperimentLabel(label); if (samples) await playFloatSamples(samples);
}

function submitExperimentAnswer(answer) {
  const session=experimentState.session, trial=currentExperimentTrial();
  if (!trial || trial.response || session?.on_break) return;
  if (!['A','B','X'].every(k=>trial.play_counts[k]>0)) { toast('請至少播放 A、B、X 各一次'); return; }
  const rt=Math.max(0,Date.now()-(trial.started_at_ms??Date.now()));
  trial.response={answer,correct:answer===trial.correct_answer,rt_ms:rt,submitted_at:new Date().toISOString()};
  updateExperimentUI();
}

function shouldBreakAfterCurrent(session, trial) {
  if (!session.break_every || trial.is_practice) return false;
  const answeredMain=session.trials.filter(t=>!t.is_practice&&t.response).length;
  const remainingMain=session.trials.some((t,i)=>i>experimentState.currentIndex&&!t.is_practice);
  return remainingMain && answeredMain>0 && answeredMain % session.break_every === 0;
}

function advanceExperimentTrial() {
  const session=experimentState.session, trial=currentExperimentTrial();
  if (!session) return;
  if (session.on_break) { session.on_break=false; updateExperimentUI(); return; }
  if (!trial?.response) return;
  if (experimentState.currentIndex >= session.trials.length-1) session.completed_at=new Date().toISOString();
  else {
    const takeBreak=shouldBreakAfterCurrent(session,trial);
    experimentState.currentIndex++;
    if (takeBreak) { session.on_break=true; session.break_count++; }
  }
  updateExperimentUI();
}

function experimentManifest() {
  const session=experimentState.session; if(!session)return null;
  const summary=experimentSummary(session);
  return {
    farhp_weblab_study_version:'0.6', session_id:session.session_id, study_id:session.study_id,
    participant_id:session.participant_id, created_at:session.created_at, completed_at:session.completed_at,
    task:session.task,
    setup:{seed:session.seed,repeats_per_stimulus:session.repeats,practice_trials:session.practice_count,break_every_main_trials:session.break_every,
      selected_stimuli:session.selected_stimuli,participant_latin_row:session.participant_latin_row,ordering_method:session.ordering_method,
      baseline_condition:'current_utterance_farhp',altered_condition:session.altered_condition,altered_condition_label:session.altered_condition_label,
      intervention_strength:session.strength,randomization:'balanced_ABX_cells_plus_participant_indexed_stimulus_order',
      blinding:'formal-trial A/B mapping and correctness hidden until completion'},
    invariant_certificates:session.invariant_certificates,
    stimuli:Object.values(session.stimulus_pool).map(s=>({stimulus_key:s.key,label:s.label,bopomofo:s.bopomofo,duration_seconds:s.duration_seconds,source_utterance:s.source_manifest,invariant_certificate:s.invariant_certificate})),
    trials:session.trials.map(t=>({sequence_index:t.sequence_index,trial:t.trial,is_practice:t.is_practice,practice_ordinal:t.practice_ordinal??null,main_ordinal:t.main_ordinal??null,
      stimulus_key:t.stimulus_key,a_condition:t.a_condition,b_condition:t.b_condition,x_condition:t.x_condition,correct_answer:t.correct_answer,
      play_counts:t.play_counts,response:t.response})),
    summary:{practice_answered:summary.practiceAnswered,answered_main_trials:summary.answered,correct_main_trials:summary.correct,main_accuracy:summary.accuracy,
      median_main_response_time_ms:summary.medianRtMs,total_replays:summary.totalReplays,breaks_taken:session.break_count},
    privacy_note:'participant_id must be an anonymous research code; do not store names, emails or contact details',
    warning:'offline synthetic-speech research MVP; not a substitute for ethics review, informed consent or population-level validation',
  };
}

function experimentCsv() {
  const m=experimentManifest(); if(!m)return '';
  const header=['session_id','study_id','participant_id','sequence_index','phase','main_ordinal','stimulus_key','a_condition','b_condition','x_condition','correct_answer','response','correct','rt_ms','plays_a','plays_b','plays_x'];
  const rows=m.trials.map(t=>[m.session_id,m.study_id,m.participant_id,t.sequence_index,t.is_practice?'practice':'main',t.main_ordinal??'',t.stimulus_key,t.a_condition,t.b_condition,t.x_condition,t.correct_answer,t.response?.answer??'',t.response?.correct??'',t.response?.rt_ms??'',t.play_counts.A,t.play_counts.B,t.play_counts.X]);
  return [header,...rows].map(row=>row.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n');
}

function conditionRevealLabel(condition,session){return condition==='baseline'?'基準':session.altered_condition_label;}

function renderExperimentLog(){
  const host=$('#experimentLog'),session=experimentState.session;if(!host||!session)return;
  const completed=Boolean(session.completed_at),rows=session.trials.filter(t=>t.response);
  if(!rows.length){host.innerHTML='<tr><td colspan="6">尚無紀錄</td></tr>';return;}
  host.innerHTML=rows.map(t=>{
    const replay=Object.values(t.play_counts).reduce((s,n)=>s+Math.max(0,n-1),0);
    const reveal=completed||t.is_practice;
    const result=reveal?(t.response.correct?'正確':'錯誤'):'已封存';
    const mapping=reveal?`A=${conditionRevealLabel(t.a_condition,session)}；B=${conditionRevealLabel(t.b_condition,session)}；X=${conditionRevealLabel(t.x_condition,session)}`:'隱藏';
    const phase=t.is_practice?`練習 ${t.practice_ordinal}`:`正式 ${t.main_ordinal}`;
    return `<tr><td>${phase}<br><small>${STUDY_STIMULUS_MAP[t.stimulus_key]?.label??t.stimulus_key}</small></td><td>X = ${t.response.answer}</td><td class="${reveal?(t.response.correct?'ok':'bad'):''}">${result}</td><td>${(t.response.rt_ms/1000).toFixed(2)} s</td><td>${replay}</td><td>${mapping}</td></tr>`;
  }).join('');
}

function updateExperimentUILegacy(){
  const session=experimentState.session,trial=currentExperimentTrial();
  $('#experimentStrengthOut').value=`${Math.round(Number($('#experimentStrength').value)*100)}%`;
  $('#studyRepeatsOut').value=`${$('#studyRepeats').value} 次`;
  const blocked=!session||Boolean(session.completed_at)||Boolean(trial?.response)||Boolean(session?.on_break);
  ['#playStimA','#playStimB','#playStimX','#answerA','#answerB'].forEach(sel=>{$(sel).disabled=blocked;});
  const canNext=Boolean(session?.on_break)||Boolean(trial?.response);
  $('#nextExperimentTrial').disabled=!canNext||Boolean(session?.completed_at);
  $('#experimentJsonBtn').disabled=!session?.completed_at;$('#experimentCsvBtn').disabled=!session?.completed_at;
  if(!session||!trial){
    $('#experimentProgress').textContent='0 / 0';$('#experimentPhase').textContent='—';$('#experimentAccuracy').textContent='—';$('#experimentMedianRt').textContent='—';
    $('#experimentStateBadge').textContent='尚未開始';$('#experimentTrialBadge').textContent='Trial —';$('#experimentStimulusBadge').textContent='刺激 —';
    $('#experimentFeedback').className='test-result neutral';$('#experimentFeedback').textContent='建立研究後，請先完成練習輪，再進入正式盲化試驗。';return;
  }
  const summary=experimentSummary(session),stim=STUDY_STIMULUS_MAP[trial.stimulus_key];
  $('#experimentProgress').textContent=`${summary.answered} / ${summary.mainTotal}`;
  $('#experimentPhase').textContent=session.on_break?'休息':(trial.is_practice?`練習 ${trial.practice_ordinal}/${session.practice_count}`:`正式 ${trial.main_ordinal}/${summary.mainTotal}`);
  $('#experimentAccuracy').textContent=session.completed_at?(summary.accuracy==null?'—':`${Math.round(summary.accuracy*100)}%`):'封存';
  $('#experimentMedianRt').textContent=summary.medianRtMs==null?'—':`${(summary.medianRtMs/1000).toFixed(2)} s`;
  $('#experimentStateBadge').textContent=session.completed_at?'已完成／可匯出':session.on_break?'休息節點':trial.is_practice?'練習中／即時回饋':'正式研究／映射封存';
  $('#experimentTrialBadge').textContent=trial.is_practice?`Practice ${trial.practice_ordinal}`:`Trial ${trial.main_ordinal}`;
  $('#experimentTrialBadge').className=`status-badge ${trial.is_practice?'practice-badge':''}`;
  $('#experimentStimulusBadge').textContent=`${stim?.label??trial.stimulus_key}｜${stim?.bopomofo??''}`;
  $('#playCountA').textContent=`${trial.play_counts.A} 次`;$('#playCountB').textContent=`${trial.play_counts.B} 次`;$('#playCountX').textContent=`${trial.play_counts.X} 次`;
  const certs=session.invariant_certificates,passed=certs.filter(x=>x.pass).length,maxF0=Math.max(...certs.map(x=>x.max_f0_track_difference_hz));
  $('#experimentInvariant').className=`test-result ${session.invariant_pass?'pass':'fail'}`;
  $('#experimentInvariant').textContent=`${session.invariant_pass?'PASS':'CHECK'}｜${passed}/${certs.length} 刺激通過・f₀ 最大差 ${maxF0.toExponential(2)} Hz・順序列 ${session.participant_latin_row}`;
  const feedback=$('#experimentFeedback');
  if(session.completed_at){feedback.className='test-result pass';feedback.textContent=`研究完成：正式輪 ${summary.correct}/${summary.answered} 正確，正確率 ${Math.round((summary.accuracy??0)*100)}%。可匯出研究資料。`;}
  else if(session.on_break){feedback.className='test-result neutral break-screen';feedback.textContent=`休息節點 ${session.break_count}：請短暫休息，準備好後按「結束休息並繼續」。`;}
  else if(trial.response&&trial.is_practice){feedback.className=`test-result ${trial.response.correct?'pass':'fail'}`;feedback.textContent=`練習回饋：${trial.response.correct?'正確':'錯誤'}。X = ${trial.correct_answer}；此輪不納入正式統計。`;}
  else if(trial.response){feedback.className='test-result neutral';feedback.textContent='正式輪回答已封存；完成整個研究前不揭示正確性與條件映射。';}
  else{feedback.className='test-result neutral';feedback.textContent=trial.is_practice?'練習輪：請播放 A、B、X；提交後會立即顯示正確答案。':'正式輪：請播放 A、B、X，判斷 X 與哪一個刺激完全相同。';}
  if(session.on_break) $('#nextExperimentTrial').textContent='結束休息並繼續';
  else if(experimentState.currentIndex===session.trials.length-1) $('#nextExperimentTrial').textContent='完成並揭示';
  else $('#nextExperimentTrial').textContent='下一輪';
  renderExperimentLog();
}

function logChoose(n,k){k=Math.min(k,n-k);let s=0;for(let i=1;i<=k;i++)s+=Math.log(n-k+i)-Math.log(i);return s;}
function binomialTwoSidedP(k,n,p=.5){
  if(!n)return null;const logObs=logChoose(n,k)+k*Math.log(p)+(n-k)*Math.log(1-p);let sum=0;
  for(let j=0;j<=n;j++){const lp=logChoose(n,j)+j*Math.log(p)+(n-j)*Math.log(1-p);if(lp<=logObs+1e-12)sum+=Math.exp(lp);}
  return Math.min(1,sum);
}
function wilsonInterval(k,n,z=1.959963984540054){
  if(!n)return [null,null];const ph=k/n,z2=z*z,den=1+z2/n,center=(ph+z2/(2*n))/den,half=z*Math.sqrt(ph*(1-ph)/n+z2/(4*n*n))/den;return [Math.max(0,center-half),Math.min(1,center+half)];
}

function mergeStudyManifests(manifests){
  const seenSessions=new Set(),valid=[];
  for(const m of manifests){
    if(m?.farhp_weblab_study_version!=='0.6'||!Array.isArray(m.trials)||!m.session_id||seenSessions.has(m.session_id))continue;
    seenSessions.add(m.session_id);valid.push(m);
  }
  const participantIds=new Set(valid.map(m=>`${m.study_id}::${m.participant_id}`));
  const studyIds=[...new Set(valid.map(m=>m.study_id))];
  const main=[];
  for(const m of valid)for(const t of m.trials)if(!t.is_practice&&t.response)main.push({...t,study_id:m.study_id,participant_id:m.participant_id,participant_key:`${m.study_id}::${m.participant_id}`,altered_condition:m.setup?.altered_condition??'unknown'});
  const correct=main.filter(t=>t.response.correct).length,n=main.length,[lo,hi]=wilsonInterval(correct,n),p=binomialTwoSidedP(correct,n,.5);
  const groups=new Map();
  for(const t of main){const key=`${t.altered_condition}::${t.stimulus_key}`;if(!groups.has(key))groups.set(key,{condition:t.altered_condition,stimulus_key:t.stimulus_key,participants:new Set(),trials:0,correct:0,rts:[]});const g=groups.get(key);g.participants.add(t.participant_key);g.trials++;g.correct+=t.response.correct?1:0;g.rts.push(t.response.rt_ms);}
  const byGroup=[...groups.values()].map(g=>({condition:g.condition,stimulus_key:g.stimulus_key,stimulus_label:STUDY_STIMULUS_MAP[g.stimulus_key]?.label??g.stimulus_key,participant_count:g.participants.size,trials:g.trials,correct:g.correct,accuracy:g.trials?g.correct/g.trials:null,median_rt_ms:median(g.rts)}));
  return {farhp_weblab_group_version:'0.6',created_at:new Date().toISOString(),study_ids:studyIds,source_files:valid.length,duplicate_sessions_ignored:manifests.length-valid.length,participant_count:participantIds.size,main_trials:n,correct_trials:correct,accuracy:n?correct/n:null,wilson_95:[lo,hi],binomial_two_sided_p:p,chance_probability:.5,by_condition_and_stimulus:byGroup,warning:'descriptive browser aggregation; independence, recruitment quality and multiplicity require separate research review'};
}
function groupAnalysisCsv(g=experimentState.groupAnalysis){if(!g)return'';const h=['condition','stimulus_key','stimulus_label','participant_count','trials','correct','accuracy','median_rt_ms'];return[h,...g.by_condition_and_stimulus.map(x=>h.map(k=>x[k]??''))].map(r=>r.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n');}
function renderGroupAnalysis(){
  const g=experimentState.groupAnalysis;if(!g)return;
  $('#groupParticipants').textContent=g.participant_count;$('#groupTrials').textContent=g.main_trials;$('#groupAccuracy').textContent=g.accuracy==null?'—':`${(g.accuracy*100).toFixed(1)}%`;
  $('#groupWilson').textContent=g.wilson_95[0]==null?'—':`${(g.wilson_95[0]*100).toFixed(1)}–${(g.wilson_95[1]*100).toFixed(1)}%`;
  $('#groupPValue').textContent=g.binomial_two_sided_p==null?'—':g.binomial_two_sided_p.toExponential(3);
  $('#groupAnalysisState').className=`test-result ${g.source_files?'pass':'fail'}`;$('#groupAnalysisState').textContent=`已合併 ${g.source_files} 份有效檔案、${g.participant_count} 位匿名受試者；機率基準為 50%。`;
  $('#groupAnalysisRows').innerHTML=g.by_condition_and_stimulus.map(x=>`<tr><td>${EXPERIMENT_CONDITION_LABELS[x.condition]??x.condition}／${x.stimulus_label}</td><td>${x.participant_count}</td><td>${x.trials}</td><td>${x.correct}</td><td>${(x.accuracy*100).toFixed(1)}%</td><td>${x.median_rt_ms==null?'—':(x.median_rt_ms/1000).toFixed(2)+' s'}</td></tr>`).join('')||'<tr><td colspan="6">沒有可分析的正式輪</td></tr>';
  $('#groupJsonBtn').disabled=false;$('#groupCsvBtn').disabled=false;
}
async function importGroupFiles(){
  const files=[...$('#groupJsonInput').files];if(!files.length){toast('請先選擇研究 JSON');return;}
  const manifests=[];for(const f of files){try{manifests.push(JSON.parse(await f.text()));}catch(e){console.warn('invalid JSON',f.name,e);}}
  experimentState.groupAnalysis=mergeStudyManifests(manifests);renderGroupAnalysis();
}

function initExperimentLab(){
  const pool=$('#stimulusPool');pool.innerHTML=STUDY_STIMULI.map((s,i)=>`<label class="stimulus-choice"><input type="checkbox" value="${s.key}" ${experimentState.selectedStimuli.includes(s.key)?'checked':''}><span><b>${s.label}</b><br><small>${s.bopomofo}</small></span></label>`).join('');
  $('#generateParticipantBtn').addEventListener('click',()=>{$('#participantId').value=participantCode();});
  $('#experimentCondition').addEventListener('change',e=>{experimentState.condition=e.target.value;});
  $('#experimentStrength').addEventListener('input',e=>{experimentState.strength=Number(e.target.value);updateExperimentUI();});
  $('#studyRepeats').addEventListener('input',e=>{experimentState.repeats=Number(e.target.value);updateExperimentUI();});
  $('#experimentSeed').addEventListener('change',e=>{experimentState.seed=Math.max(1,Number(e.target.value)||20260731);});
  $('#startExperimentBtn').addEventListener('click',buildExperimentSession);$('#stopExperimentAudioBtn').addEventListener('click',stopAudio);
  $('#playStimA').addEventListener('click',()=>playExperimentStimulus('A'));$('#playStimB').addEventListener('click',()=>playExperimentStimulus('B'));$('#playStimX').addEventListener('click',()=>playExperimentStimulus('X'));
  $('#answerA').addEventListener('click',()=>submitExperimentAnswer('A'));$('#answerB').addEventListener('click',()=>submitExperimentAnswer('B'));$('#nextExperimentTrial').addEventListener('click',advanceExperimentTrial);
  $('#experimentJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(experimentManifest(),null,2)],{type:'application/json'}),'farhp_multistimulus_study.json'));
  $('#experimentCsvBtn').addEventListener('click',()=>objectUrlDownload(new Blob([experimentCsv()],{type:'text/csv;charset=utf-8'}),'farhp_multistimulus_trials.csv'));
  $('#mergeGroupBtn').addEventListener('click',importGroupFiles);
  $('#groupJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(experimentState.groupAnalysis,null,2)],{type:'application/json'}),'farhp_group_analysis.json'));
  $('#groupCsvBtn').addEventListener('click',()=>objectUrlDownload(new Blob([groupAnalysisCsv()],{type:'text/csv;charset=utf-8'}),'farhp_group_analysis.csv'));
  updateExperimentUI();
}


/* v0.8 research governance layer */
Object.assign(experimentState, {
  studyId: 'FARHP-PERCEPT-v0.8',
  plan: null,
  planDraftCreatedAt: null,
  checkpointAvailable: false,
  checkpointSavedAt: null,
});

const DEFAULT_EXCLUSION_POLICY = Object.freeze({
  min_rt_ms: 150,
  max_rt_ms: 30000,
  min_completion_ratio: 1,
  min_valid_trial_ratio: .8,
  min_plays_each_label: 1,
  accuracy_based_exclusion: false,
});

function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${stableStringify(value[k])}`).join(',')}}`;
}

async function planFingerprint(payload, preferredAlgorithm = null) {
  const text = stableStringify(payload);
  const fallback = () => ({algorithm:'FNV32x8-fallback', value:Array.from({length:8},(_,i)=>hashString32(`${i}|${text}`).toString(16).padStart(8,'0')).join('')});
  if (preferredAlgorithm === 'FNV32x8-fallback') return fallback();
  if (globalThis.crypto?.subtle && typeof TextEncoder !== 'undefined') {
    const bytes = new TextEncoder().encode(text);
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return {algorithm:'SHA-256', value:[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('')};
  }
  if (preferredAlgorithm === 'SHA-256') throw new Error('目前環境無法驗證 SHA-256 計畫指紋');
  return fallback();
}

function safeStorageGet(key) { try { return localStorage.getItem(key); } catch (_) { return null; } }
function safeStorageSet(key, value) { try { localStorage.setItem(key, value); return true; } catch (_) { return false; } }
function safeStorageRemove(key) { try { localStorage.removeItem(key); return true; } catch (_) { return false; } }
function checkpointStorageKey(studyId = $('#studyId')?.value, participantId = $('#participantId')?.value) {
  return `farhp-v0.8-checkpoint:${String(studyId||'').trim()}:${String(participantId||'').trim()}`;
}

function exclusionPolicyFromUi() {
  const minRt = Math.max(0, Number($('#minRtMs')?.value ?? DEFAULT_EXCLUSION_POLICY.min_rt_ms));
  const maxRt = Math.max(minRt + 1, Number($('#maxRtMs')?.value ?? DEFAULT_EXCLUSION_POLICY.max_rt_ms));
  return {
    min_rt_ms:minRt,
    max_rt_ms:maxRt,
    min_completion_ratio:clamp(Number($('#minCompletionRatio')?.value ?? 1),0,1),
    min_valid_trial_ratio:clamp(Number($('#minValidTrialRatio')?.value ?? .8),0,1),
    min_plays_each_label:1,
    accuracy_based_exclusion:false,
  };
}

function planPayloadFromUi() {
  const selected = selectedStimulusKeys();
  return {
    farhp_weblab_plan_version:'0.8',
    study_id:($('#studyId')?.value || 'FARHP-PERCEPT-v0.8').trim(),
    task:'multi_stimulus_ABX_identity_match',
    planned_sample_size:Math.max(1,Number($('#plannedSampleSize')?.value)||24),
    primary_endpoint:$('#primaryEndpoint')?.value || 'abx_accuracy_vs_0_5',
    preregistration_note:($('#preregistrationNote')?.value || '').trim(),
    design:{
      selected_stimuli:selected,
      altered_condition:$('#experimentCondition')?.value || 'zero',
      intervention_strength:Number($('#experimentStrength')?.value ?? 1),
      repeats_per_stimulus:Number($('#studyRepeats')?.value ?? 1),
      practice_trials:Number($('#practiceTrials')?.value ?? 0),
      break_every_main_trials:Number($('#breakEvery')?.value ?? 0),
      seed:Math.max(1,Number($('#experimentSeed')?.value)||20260731),
      ordering:'participant_indexed_latin_or_cyclic_order_plus_balanced_ABX_cells',
      blinding:'formal-trial A/B mapping and correctness hidden until completion',
    },
    exclusion_policy:exclusionPolicyFromUi(),
    governance:{
      research_role:$('#researchRole')?.value || 'principal_investigator',
      consent_template:{
        version:($('#consentVersion')?.value || 'FARHP-CONSENT-v0.8').trim(),
        title:($('#consentTitle')?.value || 'FARHP 相位知覺研究參與同意').trim(),
        summary:($('#consentSummary')?.value || '').trim(),
        affirmative_consent_required:true, eligibility_attestation_required:true
      },
      direct_identifiers_forbidden:true, local_processing_only:true,
      audit_policy:{live_chain:'FNV32x8-live',sealed_chain:'SHA-256-when-available'},
      deidentification_policy:'study-specific one-way pseudonym for analysis export'
    },
  };
}

function researchPlanManifest() {
  if (experimentState.plan) return JSON.parse(JSON.stringify(experimentState.plan));
  const payload=planPayloadFromUi();
  return {...payload,status:'draft',created_at:experimentState.planDraftCreatedAt ?? new Date().toISOString(),locked_at:null,plan_fingerprint:null};
}

function setPlanControlsLocked(locked) {
  $$('[data-plan-control]').forEach(el=>{el.disabled=locked;});
  const pool=$('#stimulusPool'); if(pool){pool.classList.toggle('locked',locked); $$(`#stimulusPool input`).forEach(el=>{el.disabled=locked;});}
  $('#lockPlanBtn').disabled=locked;
  $('#duplicatePlanBtn').disabled=!locked;
}

function applyPlanToUi(plan) {
  const d=plan.design||{};
  $('#studyId').value=plan.study_id||'FARHP-PERCEPT-v0.8';
  $('#plannedSampleSize').value=plan.planned_sample_size??24;
  $('#primaryEndpoint').value=plan.primary_endpoint||'abx_accuracy_vs_0_5';
  $('#preregistrationNote').value=plan.preregistration_note||'';
  const gov=plan.governance||{},ct=gov.consent_template||{};
  if($('#researchRole'))$('#researchRole').value=gov.research_role||'principal_investigator';
  if($('#consentVersion'))$('#consentVersion').value=ct.version||'FARHP-CONSENT-v0.8';
  if($('#consentTitle'))$('#consentTitle').value=ct.title||'FARHP 相位知覺研究參與同意';
  if($('#consentSummary'))$('#consentSummary').value=ct.summary||'';
  $('#experimentCondition').value=d.altered_condition||'zero';
  $('#experimentStrength').value=d.intervention_strength??1;
  $('#studyRepeats').value=d.repeats_per_stimulus??1;
  $('#practiceTrials').value=d.practice_trials??0;
  $('#breakEvery').value=d.break_every_main_trials??0;
  $('#experimentSeed').value=d.seed??20260731;
  const ep=plan.exclusion_policy||DEFAULT_EXCLUSION_POLICY;
  $('#minRtMs').value=ep.min_rt_ms??150; $('#maxRtMs').value=ep.max_rt_ms??30000;
  $('#minCompletionRatio').value=ep.min_completion_ratio??1; $('#minValidTrialRatio').value=ep.min_valid_trial_ratio??.8;
  const selected=new Set(d.selected_stimuli||[]); $$('#stimulusPool input').forEach(x=>{x.checked=selected.has(x.value);});
  experimentState.selectedStimuli=[...selected];
  experimentState.plan=JSON.parse(JSON.stringify(plan));
  setPlanControlsLocked(plan.status==='locked');
  updateExperimentUI();
}

async function lockResearchPlan() {
  const payload=planPayloadFromUi();
  if(!payload.study_id){toast('研究 ID 不可為空');return null;}
  if(payload.design.selected_stimuli.length<2){toast('研究計畫至少需要兩組刺激');return null;}
  if(payload.exclusion_policy.max_rt_ms<=payload.exclusion_policy.min_rt_ms){toast('最長 RT 必須大於最短 RT');return null;}
  const created=experimentState.planDraftCreatedAt??new Date().toISOString();
  const fingerprint=await planFingerprint(payload);
  experimentState.plan={...payload,status:'locked',created_at:created,locked_at:new Date().toISOString(),plan_fingerprint:fingerprint};
  setPlanControlsLocked(true); updateExperimentUI(); toast(`研究計畫已鎖定：${fingerprint.value.slice(0,12)}`);
  return experimentState.plan;
}

function duplicateResearchPlan() {
  const plan=researchPlanManifest();
  plan.status='draft'; plan.locked_at=null; plan.plan_fingerprint=null; plan.created_at=new Date().toISOString();
  plan.study_id=`${plan.study_id}-COPY`;
  experimentState.plan=null; experimentState.planDraftCreatedAt=plan.created_at; applyPlanToUi(plan); experimentState.plan=null; setPlanControlsLocked(false);
  experimentState.session=null; experimentState.currentIndex=0; updateExperimentUI(); toast('已複製為可編輯的新研究計畫');
}

async function importResearchPlanFile(file) {
  const plan=JSON.parse(await file.text());
  if(plan?.farhp_weblab_plan_version!=='0.8') throw new Error('不是 v0.8 研究計畫');
  if(plan.status==='locked') {
    const expected=await planFingerprint({farhp_weblab_plan_version:plan.farhp_weblab_plan_version,study_id:plan.study_id,task:plan.task,planned_sample_size:plan.planned_sample_size,primary_endpoint:plan.primary_endpoint,preregistration_note:plan.preregistration_note,design:plan.design,exclusion_policy:plan.exclusion_policy,governance:plan.governance}, plan.plan_fingerprint?.algorithm);
    if(!plan.plan_fingerprint?.value || expected.value!==plan.plan_fingerprint.value) throw new Error('研究計畫指紋不一致');
  }
  applyPlanToUi(plan); toast(plan.status==='locked'?'已載入並驗證鎖定計畫':'已載入草稿計畫');
}

function checkpointManifest() {
  const session=experimentState.session;if(!session)return null;
  return {
    farhp_weblab_checkpoint_version:'0.8',saved_at:new Date().toISOString(),plan:researchPlanManifest(),
    session:{session_id:session.session_id,study_id:session.study_id,participant_id:session.participant_id,created_at:session.created_at,completed_at:session.completed_at,current_index:experimentState.currentIndex,on_break:session.on_break,break_count:session.break_count,governance:session.governance||null,audit_log:session.audit_log||[],
      trials:session.trials.map(t=>({sequence_index:t.sequence_index,play_counts:{...t.play_counts},started_at_ms:t.started_at_ms,response:t.response?{answer:t.response.answer,rt_ms:t.response.rt_ms,submitted_at:t.response.submitted_at}:null}))},
    privacy_note:'contains anonymous code and responses only; no audio arrays or direct identifiers',
  };
}

function persistCheckpoint() {
  const cp=checkpointManifest(); if(!cp)return false;
  const ok=safeStorageSet(checkpointStorageKey(cp.session.study_id,cp.session.participant_id),JSON.stringify(cp));
  experimentState.checkpointAvailable=ok; experimentState.checkpointSavedAt=cp.saved_at; renderDeploymentUI(); return ok;
}

function clearLocalCheckpoint() {
  const ok=safeStorageRemove(checkpointStorageKey()); experimentState.checkpointAvailable=false;experimentState.checkpointSavedAt=null;renderDeploymentUI();toast(ok?'本機檢查點已清除':'無法存取瀏覽器儲存空間');
}

function restoreCheckpointProgress(checkpoint) {
  const session=experimentState.session, saved=checkpoint.session;
  if(!session||!saved)return false;
  const bySeq=new Map((saved.trials||[]).map(t=>[t.sequence_index,t]));
  for(const t of session.trials){const x=bySeq.get(t.sequence_index);if(!x)continue;t.play_counts={A:Number(x.play_counts?.A||0),B:Number(x.play_counts?.B||0),X:Number(x.play_counts?.X||0)};t.started_at_ms=x.started_at_ms??null;if(x.response){t.response={answer:x.response.answer,correct:x.response.answer===t.correct_answer,rt_ms:Number(x.response.rt_ms||0),submitted_at:x.response.submitted_at||new Date().toISOString()};}}
  session.session_id=saved.session_id;session.created_at=saved.created_at;session.completed_at=saved.completed_at??null;session.on_break=Boolean(saved.on_break);session.break_count=Number(saved.break_count||0);session.governance=saved.governance||session.governance;session.audit_log=Array.isArray(saved.audit_log)?saved.audit_log:session.audit_log||[];
  experimentState.currentIndex=clamp(Number(saved.current_index||0),0,Math.max(0,session.trials.length-1));
  experimentState.checkpointAvailable=true;experimentState.checkpointSavedAt=checkpoint.saved_at;updateExperimentUI();persistCheckpoint();return true;
}

function resumeFromCheckpoint(checkpoint) {
  if(checkpoint?.farhp_weblab_checkpoint_version!=='0.8'||!checkpoint.plan||!checkpoint.session) throw new Error('不是 v0.8 檢查點');
  applyPlanToUi(checkpoint.plan); $('#participantId').value=checkpoint.session.participant_id;
  const session=buildExperimentSession({checkpoint,quiet:true}); if(!session)throw new Error('無法重建工作階段');
  restoreCheckpointProgress(checkpoint); toast('工作階段已依計畫與種子重建並恢復'); return session;
}

function trialQualityCertificate(trial,policy=DEFAULT_EXCLUSION_POLICY) {
  const reasons=[];
  if(!trial.response) reasons.push('missing_response');
  else {if(trial.response.rt_ms<policy.min_rt_ms)reasons.push('rt_too_fast');if(trial.response.rt_ms>policy.max_rt_ms)reasons.push('rt_too_slow');}
  for(const key of ['A','B','X']) if((trial.play_counts?.[key]||0)<(policy.min_plays_each_label??1)) reasons.push(`insufficient_play_${key}`);
  return {included:reasons.length===0,reasons};
}

function evaluateStudyManifest(manifest) {
  const embedded=manifest.exclusion_policy||manifest.plan?.exclusion_policy;
  const legacyPolicy=manifest?.farhp_weblab_study_version==='0.6'&&!embedded?{min_rt_ms:0,max_rt_ms:Number.MAX_SAFE_INTEGER,min_completion_ratio:0,min_valid_trial_ratio:0,min_plays_each_label:0,accuracy_based_exclusion:false}:{};
  const policy={...DEFAULT_EXCLUSION_POLICY,...legacyPolicy,...(embedded||{})};
  const main=(manifest.trials||[]).filter(t=>!t.is_practice),answered=main.filter(t=>t.response);
  const trialCertificates=main.map((t,i)=>({sequence_index:t.sequence_index??i+1,stimulus_key:t.stimulus_key,...trialQualityCertificate(t,policy)}));
  const valid=trialCertificates.filter(x=>x.included).length,completion=main.length?answered.length/main.length:0,validRatio=main.length?valid/main.length:0,reasons=[];
  if(completion<policy.min_completion_ratio)reasons.push('completion_ratio_below_plan');
  if(validRatio<policy.min_valid_trial_ratio)reasons.push('valid_trial_ratio_below_plan');
  return {included:reasons.length===0,reasons,completion_ratio:completion,valid_trial_ratio:validRatio,main_trials:main.length,answered_trials:answered.length,valid_trials:valid,trial_certificates:trialCertificates,policy};
}

function buildExperimentSession(options={}) {
  if(!experimentState.plan||experimentState.plan.status!=='locked'){toast('請先鎖定研究計畫');return null;}
  const plan=experimentState.plan,d=plan.design;
  experimentState.condition=d.altered_condition;experimentState.strength=d.intervention_strength;experimentState.repeats=d.repeats_per_stimulus;experimentState.practiceCount=d.practice_trials;experimentState.breakEvery=d.break_every_main_trials;experimentState.seed=d.seed;
  experimentState.studyId=plan.study_id;experimentState.participantId=($('#participantId').value||participantCode()).trim();experimentState.selectedStimuli=d.selected_stimuli.slice();
  if(!experimentState.participantId){toast('匿名受試者 ID 不可為空');return null;}
  if(!options.checkpoint && (!$('#eligibilityAttest')?.checked || !$('#consentAttest')?.checked)){toast('開始前必須完成電子同意與資格確認');return null;}
  if($('#withdrawalCode') && $('#withdrawalCode').value==='尚未產生') $('#withdrawalCode').value=makeWithdrawalCode();
  const stimulusPool={},certificates=[];
  for(let i=0;i<experimentState.selectedStimuli.length;i++){
    const key=experimentState.selectedStimuli[i],baseSeed=(experimentState.seed+hashString32(key)+i*104729)>>>0;
    const baselinePack=synthesizeStudyStimulus(key,'identity',1,baseSeed),alteredPack=synthesizeStudyStimulus(key,experimentState.condition,experimentState.strength,baseSeed+65537);
    const certificate={stimulus_key:key,...stimulusInvariantCertificate(baselinePack.audio,alteredPack.audio)};
    stimulusPool[key]={key,label:STUDY_STIMULUS_MAP[key].label,bopomofo:STUDY_STIMULUS_MAP[key].bopomofo,source_manifest:baselinePack.sourceManifest,audio:{baseline:baselinePack.audio.samples,altered:alteredPack.audio.samples},invariant_certificate:certificate,duration_seconds:baselinePack.audio.duration};certificates.push(certificate);
  }
  const planTrials=buildStudyTrialPlan(experimentState.selectedStimuli,experimentState.repeats,experimentState.practiceCount,experimentState.participantId,experimentState.seed);
  experimentState.session={session_id:`${experimentState.studyId}-${experimentState.participantId}-${experimentState.seed}-${Date.now()}`,study_id:experimentState.studyId,participant_id:experimentState.participantId,created_at:new Date().toISOString(),completed_at:null,task:'multi_stimulus_ABX_identity_match',seed:experimentState.seed,plan_fingerprint:plan.plan_fingerprint,exclusion_policy:plan.exclusion_policy,altered_condition:experimentState.condition,altered_condition_label:EXPERIMENT_CONDITION_LABELS[experimentState.condition],strength:experimentState.strength,repeats:experimentState.repeats,practice_count:experimentState.practiceCount,break_every:experimentState.breakEvery,selected_stimuli:experimentState.selectedStimuli.slice(),participant_latin_row:planTrials.participantRow,ordering_method:experimentState.selectedStimuli.length%2===0?'participant_indexed_mirrored_latin_row':'participant_indexed_cyclic_latin_row',stimulus_pool:stimulusPool,invariant_certificates:certificates,invariant_pass:certificates.every(x=>x.pass),trials:planTrials.trials,on_break:false,break_count:0,
    governance:{research_role:plan.governance?.research_role||'principal_investigator',consent_record:{consent_version:plan.governance?.consent_template?.version||'FARHP-CONSENT-v0.8',consent_title:plan.governance?.consent_template?.title||'',consented_at:new Date().toISOString(),affirmative_consent:true,eligibility_attested:true,withdrawal_code:$('#withdrawalCode')?.value||null,plan_fingerprint:plan.plan_fingerprint?.value||null},direct_identifiers_collected:false},audit_log:[]};
  experimentState.currentIndex=0;appendLiveAuditEvent('plan_bound',{plan_fingerprint:plan.plan_fingerprint?.value||null});appendLiveAuditEvent('consent_recorded',{consent_version:experimentState.session.governance.consent_record.consent_version});appendLiveAuditEvent('session_started',{session_id:experimentState.session.session_id});updateExperimentUI();persistCheckpoint();if(!options.quiet)toast('鎖定計畫下的研究工作階段已建立');return experimentState.session;
}

async function playExperimentStimulus(label) {
  const session=experimentState.session,trial=currentExperimentTrial();if(!trial||trial.response||session?.on_break)return;if(trial.started_at_ms==null)trial.started_at_ms=Date.now();trial.play_counts[label]++;updateExperimentUI();persistCheckpoint();const samples=samplesForExperimentLabel(label);if(samples)await playFloatSamples(samples);
}

function submitExperimentAnswer(answer) {
  const session=experimentState.session,trial=currentExperimentTrial();if(!trial||trial.response||session?.on_break)return;if(!['A','B','X'].every(k=>trial.play_counts[k]>0)){toast('請至少播放 A、B、X 各一次');return;}const rt=Math.max(0,Date.now()-(trial.started_at_ms??Date.now()));trial.response={answer,correct:answer===trial.correct_answer,rt_ms:rt,submitted_at:new Date().toISOString()};appendLiveAuditEvent('response_submitted',{sequence_index:trial.sequence_index,is_practice:trial.is_practice,answer,rt_ms:rt});updateExperimentUI();persistCheckpoint();
}

function advanceExperimentTrial() {
  const session=experimentState.session,trial=currentExperimentTrial();if(!session)return;if(session.on_break){session.on_break=false;updateExperimentUI();persistCheckpoint();return;}if(!trial?.response)return;if(experimentState.currentIndex>=session.trials.length-1){session.completed_at=new Date().toISOString();appendLiveAuditEvent('session_completed',{completed_at:session.completed_at});}else{const takeBreak=shouldBreakAfterCurrent(session,trial);experimentState.currentIndex++;if(takeBreak){session.on_break=true;session.break_count++;appendLiveAuditEvent('break_started',{break_count:session.break_count});}}updateExperimentUI();persistCheckpoint();
}

function experimentManifest() {
  const session=experimentState.session;if(!session)return null;const summary=experimentSummary(session);
  const draft={farhp_weblab_study_version:'0.8',session_id:session.session_id,study_id:session.study_id,participant_id:session.participant_id,created_at:session.created_at,completed_at:session.completed_at,task:session.task,plan_fingerprint:session.plan_fingerprint,plan:researchPlanManifest(),exclusion_policy:session.exclusion_policy,
    setup:{seed:session.seed,repeats_per_stimulus:session.repeats,practice_trials:session.practice_count,break_every_main_trials:session.break_every,selected_stimuli:session.selected_stimuli,participant_latin_row:session.participant_latin_row,ordering_method:session.ordering_method,baseline_condition:'current_utterance_farhp',altered_condition:session.altered_condition,altered_condition_label:session.altered_condition_label,intervention_strength:session.strength,randomization:'balanced_ABX_cells_plus_participant_indexed_stimulus_order',blinding:'formal-trial A/B mapping and correctness hidden until completion'},
    invariant_certificates:session.invariant_certificates,stimuli:Object.values(session.stimulus_pool).map(s=>({stimulus_key:s.key,label:s.label,bopomofo:s.bopomofo,duration_seconds:s.duration_seconds,source_utterance:s.source_manifest,invariant_certificate:s.invariant_certificate})),
    trials:session.trials.map(t=>({sequence_index:t.sequence_index,trial:t.trial,is_practice:t.is_practice,practice_ordinal:t.practice_ordinal??null,main_ordinal:t.main_ordinal??null,stimulus_key:t.stimulus_key,a_condition:t.a_condition,b_condition:t.b_condition,x_condition:t.x_condition,correct_answer:t.correct_answer,play_counts:t.play_counts,response:t.response})),
    summary:{practice_answered:summary.practiceAnswered,answered_main_trials:summary.answered,correct_main_trials:summary.correct,main_accuracy:summary.accuracy,median_main_response_time_ms:summary.medianRtMs,total_replays:summary.totalReplays,breaks_taken:session.break_count},privacy_note:'participant_id must be an anonymous research code; do not store names, emails or contact details',warning:'offline synthetic-speech research MVP; not a substitute for ethics review, informed consent or population-level validation'};
  draft.governance=session.governance||null;draft.audit_log=session.audit_log||[];draft.audit_validation=verifyLiveAuditChain(draft.audit_log);draft.exclusion_certificate=evaluateStudyManifest(draft);return draft;
}

function experimentCsv(){const m=experimentManifest();if(!m)return'';const certBySeq=new Map((m.exclusion_certificate?.trial_certificates||[]).map(x=>[x.sequence_index,x]));const h=['session_id','study_id','participant_id','plan_fingerprint','sequence_index','phase','main_ordinal','stimulus_key','a_condition','b_condition','x_condition','correct_answer','response','correct','rt_ms','plays_a','plays_b','plays_x','included_by_policy','exclusion_reasons'];const rows=m.trials.map(t=>{const c=certBySeq.get(t.sequence_index);return[m.session_id,m.study_id,m.participant_id,m.plan_fingerprint?.value??'',t.sequence_index,t.is_practice?'practice':'main',t.main_ordinal??'',t.stimulus_key,t.a_condition,t.b_condition,t.x_condition,t.correct_answer,t.response?.answer??'',t.response?.correct??'',t.response?.rt_ms??'',t.play_counts.A,t.play_counts.B,t.play_counts.X,t.is_practice?'':c?.included??'',t.is_practice?'':(c?.reasons||[]).join('|')];});return[h,...rows].map(row=>row.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n');}

function mergeStudyManifests(manifests){
  const seen=new Set(),valid=[];for(const m of manifests){if(!['0.6','0.7','0.8'].includes(m?.farhp_weblab_study_version)||!Array.isArray(m.trials)||!m.session_id||seen.has(m.session_id))continue;seen.add(m.session_id);valid.push(m);}
  const evaluations=valid.map(m=>({manifest:m,evaluation:evaluateStudyManifest(m)}));const includedSessions=evaluations.filter(x=>x.evaluation.included),excludedSessions=evaluations.filter(x=>!x.evaluation.included);
  const main=[];for(const {manifest:m,evaluation:e} of includedSessions){const cert=new Map(e.trial_certificates.map(x=>[x.sequence_index,x]));let mainIndex=0;for(const t of m.trials){if(t.is_practice)continue;mainIndex++;const seq=t.sequence_index??mainIndex;if(t.response&&cert.get(seq)?.included)main.push({...t,sequence_index:seq,study_id:m.study_id,participant_id:m.participant_id,participant_key:`${m.study_id}::${m.participant_id}`,session_id:m.session_id,altered_condition:m.setup?.altered_condition??'unknown'});}}
  const correct=main.filter(t=>t.response.correct).length,n=main.length,[lo,hi]=wilsonInterval(correct,n),p=binomialTwoSidedP(correct,n,.5);
  const participants=new Map();for(const {manifest:m,evaluation:e} of evaluations){const key=`${m.study_id}::${m.participant_id}`;if(!participants.has(key))participants.set(key,{participant_id:m.participant_id,study_id:m.study_id,sessions:0,included_sessions:0,excluded_sessions:0,trials:0,correct:0,rts:[],reasons:new Set()});const g=participants.get(key);g.sessions++;if(e.included)g.included_sessions++;else{g.excluded_sessions++;e.reasons.forEach(r=>g.reasons.add(r));}}
  for(const t of main){const g=participants.get(t.participant_key);g.trials++;g.correct+=t.response.correct?1:0;g.rts.push(t.response.rt_ms);}
  const byParticipant=[...participants.values()].map(g=>({participant_id:g.participant_id,study_id:g.study_id,sessions:g.sessions,included_sessions:g.included_sessions,excluded_sessions:g.excluded_sessions,valid_trials:g.trials,correct:g.correct,accuracy:g.trials?g.correct/g.trials:null,median_rt_ms:median(g.rts),included:g.included_sessions>0,exclusion_reasons:[...g.reasons]}));
  const stim=new Map(),condStim=new Map();for(const t of main){if(!stim.has(t.stimulus_key))stim.set(t.stimulus_key,{stimulus_key:t.stimulus_key,participants:new Set(),trials:0,correct:0,rts:[]});const g=stim.get(t.stimulus_key);g.participants.add(t.participant_key);g.trials++;g.correct+=t.response.correct?1:0;g.rts.push(t.response.rt_ms);const ck=`${t.altered_condition}::${t.stimulus_key}`;if(!condStim.has(ck))condStim.set(ck,{condition:t.altered_condition,stimulus_key:t.stimulus_key,participants:new Set(),trials:0,correct:0,rts:[]});const c=condStim.get(ck);c.participants.add(t.participant_key);c.trials++;c.correct+=t.response.correct?1:0;c.rts.push(t.response.rt_ms);}
  const summarizeStim=g=>{const [a,b]=wilsonInterval(g.correct,g.trials);return{stimulus_key:g.stimulus_key,stimulus_label:STUDY_STIMULUS_MAP[g.stimulus_key]?.label??g.stimulus_key,participant_count:g.participants.size,trials:g.trials,correct:g.correct,accuracy:g.trials?g.correct/g.trials:null,wilson_95:[a,b],median_rt_ms:median(g.rts)}};
  const byStimulus=[...stim.values()].map(summarizeStim),byGroup=[...condStim.values()].map(g=>({...summarizeStim(g),condition:g.condition}));
  const includedParticipantKeys=new Set(main.map(t=>t.participant_key));
  return {farhp_weblab_group_version:'0.8',created_at:new Date().toISOString(),study_ids:[...new Set(valid.map(m=>m.study_id))],source_files:valid.length,duplicate_or_invalid_files_ignored:manifests.length-valid.length,included_sessions:includedSessions.length,excluded_sessions:excludedSessions.length,excluded_session_log:excludedSessions.map(x=>({session_id:x.manifest.session_id,participant_id:x.manifest.participant_id,reasons:x.evaluation.reasons,completion_ratio:x.evaluation.completion_ratio,valid_trial_ratio:x.evaluation.valid_trial_ratio})),participant_count:includedParticipantKeys.size,all_participant_count:participants.size,main_trials:n,excluded_trials:evaluations.reduce((s,x)=>s+x.evaluation.main_trials-x.evaluation.valid_trials,0),correct_trials:correct,accuracy:n?correct/n:null,wilson_95:[lo,hi],binomial_two_sided_p:p,chance_probability:.5,by_participant:byParticipant,by_stimulus:byStimulus,by_condition_and_stimulus:byGroup,warning:'descriptive browser aggregation with pre-specified process exclusions; confirmatory inference still requires an independent statistical analysis plan'};
}

function groupAnalysisCsv(g=experimentState.groupAnalysis){if(!g)return'';const rows=[['record_type','key','label','participants','sessions','trials','correct','accuracy','median_rt_ms','included','reasons'],...g.by_condition_and_stimulus.map(x=>['condition_stimulus',`${x.condition}:${x.stimulus_key}`,x.stimulus_label,x.participant_count,'',x.trials,x.correct,x.accuracy,x.median_rt_ms,'','']),...g.by_participant.map(x=>['participant',x.participant_id,x.study_id,'',x.sessions,x.valid_trials,x.correct,x.accuracy,x.median_rt_ms,x.included,x.exclusion_reasons.join('|')]),...g.by_stimulus.map(x=>['stimulus',x.stimulus_key,x.stimulus_label,x.participant_count,'',x.trials,x.correct,x.accuracy,x.median_rt_ms,'',''])];return rows.map(r=>r.map(v=>`"${String(v??'').replaceAll('"','""')}"`).join(',')).join('\n');}

function renderGroupAnalysis(){const g=experimentState.groupAnalysis;if(!g)return;$('#groupParticipants').textContent=g.participant_count;$('#groupExcluded').textContent=g.excluded_sessions;$('#groupTrials').textContent=g.main_trials;$('#groupAccuracy').textContent=g.accuracy==null?'—':`${(g.accuracy*100).toFixed(1)}%`;$('#groupWilson').textContent=g.wilson_95[0]==null?'—':`${(g.wilson_95[0]*100).toFixed(1)}–${(g.wilson_95[1]*100).toFixed(1)}%`;$('#groupPValue').textContent=g.binomial_two_sided_p==null?'—':g.binomial_two_sided_p.toExponential(3);$('#groupAnalysisState').className=`test-result ${g.source_files?'pass':'fail'}`;$('#groupAnalysisState').textContent=`${g.source_files} 份有效檔案；納入 ${g.included_sessions}、排除 ${g.excluded_sessions} 個工作階段，保留 ${g.main_trials} 個有效正式輪。`;
  $('#groupAnalysisRows').innerHTML=g.by_condition_and_stimulus.map(x=>`<tr><td>${EXPERIMENT_CONDITION_LABELS[x.condition]??x.condition}／${x.stimulus_label}</td><td>${x.participant_count}</td><td>${x.trials}</td><td>${x.correct}</td><td>${(x.accuracy*100).toFixed(1)}%</td><td>${x.median_rt_ms==null?'—':(x.median_rt_ms/1000).toFixed(2)+' s'}</td></tr>`).join('')||'<tr><td colspan="6">沒有可分析的正式輪</td></tr>';
  $('#participantAnalysisRows').innerHTML=g.by_participant.map(x=>`<tr><td>${x.participant_id}</td><td>${x.included_sessions}/${x.sessions}</td><td>${x.valid_trials}</td><td>${x.accuracy==null?'—':(x.accuracy*100).toFixed(1)+'%'}</td><td>${x.median_rt_ms==null?'—':(x.median_rt_ms/1000).toFixed(2)+' s'}</td><td class="${x.included?'ok':'bad'}">${x.included?'納入':'排除'}${x.exclusion_reasons.length?'<br><small>'+x.exclusion_reasons.join(', ')+'</small>':''}</td></tr>`).join('')||'<tr><td colspan="6">尚無資料</td></tr>';
  $('#stimulusAnalysisRows').innerHTML=g.by_stimulus.map(x=>`<tr><td>${x.stimulus_label}</td><td>${x.participant_count}</td><td>${x.trials}</td><td>${(x.accuracy*100).toFixed(1)}%</td><td>${(x.wilson_95[0]*100).toFixed(1)}–${(x.wilson_95[1]*100).toFixed(1)}%</td><td>${x.median_rt_ms==null?'—':(x.median_rt_ms/1000).toFixed(2)+' s'}</td></tr>`).join('')||'<tr><td colspan="6">尚無資料</td></tr>';$('#groupJsonBtn').disabled=false;$('#groupCsvBtn').disabled=false;}

async function importGroupFiles(){const files=[...$('#groupJsonInput').files];if(!files.length){toast('請先選擇研究 JSON');return;}const manifests=[];for(const f of files){try{manifests.push(JSON.parse(await f.text()));}catch(e){console.warn('invalid JSON',f.name,e);}}experimentState.groupAnalysis=mergeStudyManifests(manifests);renderGroupAnalysis();}

function renderDeploymentUI(){const plan=experimentState.plan,locked=plan?.status==='locked',fingerprint=plan?.plan_fingerprint?.value??'';$('#planLockBadge').textContent=locked?'已鎖定':'未鎖定';$('#planLockBadge').className=`status-badge ${locked?'locked':'neutral'}`;$('#planState').className=`test-result ${locked?'pass':'neutral'}`;$('#planState').textContent=locked?`${plan.plan_fingerprint.algorithm}｜${fingerprint}`:'尚未鎖定。正式研究必須先鎖定設計。';$('#deploymentPlanStatus').textContent=locked?'已鎖定':'未鎖定';$('#deploymentFingerprint').textContent=fingerprint||'—';const has=Boolean(safeStorageGet(checkpointStorageKey()));experimentState.checkpointAvailable=has;$('#deploymentCheckpointStatus').textContent=experimentState.checkpointSavedAt?new Date(experimentState.checkpointSavedAt).toLocaleTimeString():has?'可恢復':'尚無';$('#deploymentBadge').textContent=experimentState.session?.completed_at?'研究完成':experimentState.session?'工作階段進行中':locked?'可開始研究':'設計階段';$('#deploymentBadge').className=`status-badge ${locked?'locked':'neutral'}`;$('#checkpointExportBtn').disabled=!experimentState.session;$('#checkpointState').className=`test-result ${has||experimentState.session?'pass':'neutral'}`;$('#checkpointState').textContent=experimentState.checkpointSavedAt?`已自動保存：${new Date(experimentState.checkpointSavedAt).toLocaleString()}；不含音訊陣列。`:has?'找到目前研究／受試者的本機檢查點。':'尚無工作階段檢查點。';$('#startExperimentBtn').disabled=!locked||!consentReady();renderGovernanceUI();}

function updateExperimentUI(){renderDeploymentUI();updateExperimentUILegacy();}

function initExperimentLab(){
  const pool=$('#stimulusPool');pool.innerHTML=STUDY_STIMULI.map(s=>`<label class="stimulus-choice"><input type="checkbox" value="${s.key}" ${experimentState.selectedStimuli.includes(s.key)?'checked':''}><span><b>${s.label}</b><br><small>${s.bopomofo}</small></span></label>`).join('');
  experimentState.planDraftCreatedAt=new Date().toISOString();setPlanControlsLocked(false);
  $('#generateParticipantBtn').addEventListener('click',()=>{$('#participantId').value=participantCode();renderDeploymentUI();});
  $('#participantId').addEventListener('change',renderDeploymentUI);$('#studyId').addEventListener('change',renderDeploymentUI);
  $('#experimentStrength').addEventListener('input',updateExperimentUI);$('#studyRepeats').addEventListener('input',updateExperimentUI);
  $('#lockPlanBtn').addEventListener('click',lockResearchPlan);$('#exportPlanBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(researchPlanManifest(),null,2)],{type:'application/json'}),'farhp_research_plan_v0.8.json'));$('#duplicatePlanBtn').addEventListener('click',duplicateResearchPlan);
  $('#planJsonInput').addEventListener('change',async e=>{try{if(e.target.files[0])await importResearchPlanFile(e.target.files[0]);}catch(err){toast(`計畫載入失敗：${err.message}`);}e.target.value='';});
  $('#startExperimentBtn').addEventListener('click',()=>buildExperimentSession());$('#stopExperimentAudioBtn').addEventListener('click',stopAudio);
  $('#playStimA').addEventListener('click',()=>playExperimentStimulus('A'));$('#playStimB').addEventListener('click',()=>playExperimentStimulus('B'));$('#playStimX').addEventListener('click',()=>playExperimentStimulus('X'));$('#answerA').addEventListener('click',()=>submitExperimentAnswer('A'));$('#answerB').addEventListener('click',()=>submitExperimentAnswer('B'));$('#nextExperimentTrial').addEventListener('click',advanceExperimentTrial);
  $('#experimentJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(experimentManifest(),null,2)],{type:'application/json'}),'farhp_study_v0.8.json'));$('#experimentCsvBtn').addEventListener('click',()=>objectUrlDownload(new Blob([experimentCsv()],{type:'text/csv;charset=utf-8'}),'farhp_trials_v0.8.csv'));
  $('#checkpointExportBtn').addEventListener('click',()=>{const cp=checkpointManifest();if(cp)objectUrlDownload(new Blob([JSON.stringify(cp,null,2)],{type:'application/json'}),'farhp_checkpoint_v0.8.json');});
  $('#resumeLocalBtn').addEventListener('click',()=>{try{const raw=safeStorageGet(checkpointStorageKey());if(!raw)throw new Error('找不到目前研究／受試者的本機檢查點');resumeFromCheckpoint(JSON.parse(raw));}catch(err){toast(`恢復失敗：${err.message}`);}});
  $('#checkpointJsonInput').addEventListener('change',async e=>{try{if(e.target.files[0])resumeFromCheckpoint(JSON.parse(await e.target.files[0].text()));}catch(err){toast(`檢查點載入失敗：${err.message}`);}e.target.value='';});$('#clearCheckpointBtn').addEventListener('click',clearLocalCheckpoint);
  $('#mergeGroupBtn').addEventListener('click',importGroupFiles);$('#groupJsonBtn').addEventListener('click',()=>objectUrlDownload(new Blob([JSON.stringify(experimentState.groupAnalysis,null,2)],{type:'application/json'}),'farhp_group_analysis_v0.8.json'));$('#groupCsvBtn').addEventListener('click',()=>objectUrlDownload(new Blob([groupAnalysisCsv()],{type:'text/csv;charset=utf-8'}),'farhp_group_analysis_v0.8.csv'));
  window.addEventListener('beforeunload',()=>{if(experimentState.session)persistCheckpoint();});updateExperimentUI();
}



/* v0.8 governance, consent, audit chain and analysis exports */
Object.assign(experimentState,{roleView:'researcher',groupManifests:[]});
function makeWithdrawalCode(){const n=(Date.now()^Math.floor(Math.random()*0xffffffff))>>>0;return `WD-${n.toString(36).toUpperCase().padStart(7,'0')}`;}
function liveDigest(prev,event){const text=`${prev}|${stableStringify(event)}`;return Array.from({length:8},(_,i)=>hashString32(`${i}|${text}`).toString(16).padStart(8,'0')).join('');}
function appendLiveAuditEvent(type,payload={}){const s=experimentState.session;if(!s)return null;s.audit_log??=[];const prev=s.audit_log.at(-1)?.hash||'GENESIS';const event={index:s.audit_log.length+1,timestamp:new Date().toISOString(),type,payload,prev_hash:prev};event.hash=liveDigest(prev,{index:event.index,timestamp:event.timestamp,type:event.type,payload:event.payload});s.audit_log.push(event);renderGovernanceUI();return event;}
function verifyLiveAuditChain(events=[]){let prev='GENESIS';for(let i=0;i<events.length;i++){const e=events[i],expected=liveDigest(prev,{index:e.index,timestamp:e.timestamp,type:e.type,payload:e.payload});if(e.index!==i+1||e.prev_hash!==prev||e.hash!==expected)return{valid:false,event_count:events.length,failed_index:i+1,head:events.at(-1)?.hash||null,algorithm:'FNV32x8-live'};prev=e.hash;}return{valid:true,event_count:events.length,failed_index:null,head:events.at(-1)?.hash||null,algorithm:'FNV32x8-live'};}
async function sha256Text(text){const bytes=new TextEncoder().encode(text);if(globalThis.crypto?.subtle){const d=await crypto.subtle.digest('SHA-256',bytes);return{algorithm:'SHA-256',value:[...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('')}}return planFingerprint({text});}
async function sealAuditArchive(){const m=experimentManifest();if(!m)throw new Error('尚無研究工作階段');let prev='GENESIS';const sealed=[];for(const e of m.audit_log||[]){const payload={index:e.index,timestamp:e.timestamp,type:e.type,payload:e.payload,prev_hash:prev};const d=await sha256Text(stableStringify(payload));sealed.push({...payload,hash:d.value});prev=d.value;}const core={farhp_audit_archive_version:'0.8',created_at:new Date().toISOString(),study_id:m.study_id,session_id:m.session_id,plan_fingerprint:m.plan_fingerprint,consent_record:m.governance?.consent_record||null,study_manifest_digest:(await sha256Text(stableStringify(m))).value,event_chain:{algorithm:sealed.length?'SHA-256':'none',valid:true,event_count:sealed.length,head:sealed.at(-1)?.hash||null,events:sealed},privacy_note:'archive contains an anonymous participant code; use deidentified export for analysis sharing'};core.archive_digest=await sha256Text(stableStringify(core));return core;}
async function participantPseudonym(studyId,participantId){const d=await sha256Text(`FARHP-v0.8|${studyId}|${participantId}`);return `PID-${d.value.slice(0,20)}`;}
async function deidentifiedStudyManifest(manifest=experimentManifest()){if(!manifest)return null;const out=JSON.parse(JSON.stringify(manifest));const pseudonym=await participantPseudonym(out.study_id,out.participant_id);const sid=(await sha256Text(`SID|${out.session_id}`)).value.slice(0,20);out.farhp_weblab_study_version='0.8';out.deidentification={method:'study-specific one-way digest',algorithm:globalThis.crypto?.subtle?'SHA-256':'FNV32x8-fallback',generated_at:new Date().toISOString(),original_direct_identifiers_present:false};out.participant_id=pseudonym;out.session_id=`SID-${sid}`;if(out.governance?.consent_record){delete out.governance.consent_record.withdrawal_code;out.governance.consent_record.participant_pseudonym=pseudonym;}for(const e of out.audit_log||[]){if(e.payload?.session_id)e.payload.session_id='[redacted-session]';}return out;}
function auditRowsHtml(events=[]){return events.length?events.map(e=>`<tr><td>${e.index}</td><td>${new Date(e.timestamp).toLocaleTimeString()}</td><td>${e.type}</td><td><code>${String(e.prev_hash).slice(0,12)}</code></td><td><code>${String(e.hash).slice(0,12)}</code></td></tr>`).join(''):'<tr><td colspan="5">尚無事件</td></tr>';}
function applyRoleView(role){experimentState.roleView=role;document.body.classList.remove('role-researcher','role-participant','role-analyst');document.body.classList.add(`role-${role}`);const names={researcher:'研究者',participant:'受試者',analyst:'分析者'};$('#roleBadge').textContent=names[role]||role;$('#governanceRoleStatus').textContent=names[role]||role;if(role==='participant')location.hash='#experiment';if(role==='analyst')document.querySelector('.group-analysis-card')?.scrollIntoView({behavior:'smooth',block:'start'});}
function renderGovernanceUI(){const p=experimentState.plan,s=experimentState.session,ct=p?.governance?.consent_template;$('#consentTemplateLabel').textContent=ct?`${ct.version}｜${ct.title}`:'等待鎖定研究計畫';$('#consentText').textContent=ct?.summary||'研究計畫鎖定後，這裡會顯示已封存的同意摘要。';const consent=Boolean(s?.governance?.consent_record);$('#consentBadge').textContent=consent?'已記錄':($('#consentAttest')?.checked&&$('#eligibilityAttest')?.checked?'可開始':'未同意');$('#consentBadge').className=`status-badge ${consent?'locked':'neutral'}`;$('#consentState').className=`test-result ${consent?'pass':($('#consentAttest')?.checked&&$('#eligibilityAttest')?.checked?'pass':'neutral')}`;$('#consentState').textContent=consent?`已於 ${new Date(s.governance.consent_record.consented_at).toLocaleString()} 綁定計畫指紋。`:($('#consentAttest')?.checked&&$('#eligibilityAttest')?.checked?'同意與資格確認完成；建立研究時將寫入紀錄。':'尚未完成同意與資格確認。');const audit=verifyLiveAuditChain(s?.audit_log||[]);$('#governanceConsentStatus').textContent=consent?'已記錄':'尚未建立';$('#governanceEventCount').textContent=audit.event_count;$('#governanceChainHead').textContent=audit.head||'—';$('#governanceBadge').textContent=audit.event_count?(audit.valid?'事件鏈正常':'事件鏈異常'):'治理待命';$('#governanceBadge').className=`status-badge ${audit.event_count?(audit.valid?'locked':'warning'):'neutral'}`;$('#auditBadge').textContent=audit.event_count?`${audit.event_count} events`:'尚無事件';$('#auditBadge').className=`status-badge ${audit.valid&&audit.event_count?'locked':'neutral'}`;$('#auditRows').innerHTML=auditRowsHtml(s?.audit_log||[]);$('#auditState').className=`test-result ${audit.event_count?(audit.valid?'pass':'fail'):'neutral'}`;$('#auditState').textContent=audit.event_count?(audit.valid?`${audit.algorithm} 驗證通過；鏈頭 ${audit.head.slice(0,16)}…`:`事件 ${audit.failed_index} 驗證失敗`):'建立工作階段後開始記錄。';$('#exportAuditBtn').disabled=!s;$('#exportDeidentifiedBtn').disabled=!s;if($('#startExperimentBtn'))$('#startExperimentBtn').disabled=!(p?.status==='locked'&&consentReady());}
function consentReady(){return Boolean($('#consentAttest')?.checked&&$('#eligibilityAttest')?.checked);}
function qualityReviewManifests(manifests=[]){let missingConsent=0,auditFailures=0,planIssues=0,invariantFailures=0;const seen=new Set();let duplicates=0;for(const m of manifests){if(seen.has(m.session_id))duplicates++;seen.add(m.session_id);if(m.farhp_weblab_study_version==='0.8'){if(!m.governance?.consent_record?.affirmative_consent)missingConsent++;if(!m.audit_validation?.valid) auditFailures++;if(!m.plan_fingerprint?.value||String(m.plan_fingerprint.value).length!==64)planIssues++;}if((m.invariant_certificates||[]).some(x=>!x.pass))invariantFailures++;}const pass=missingConsent+auditFailures+planIssues+invariantFailures+duplicates===0;return{pass,files:manifests.length,missing_consent:missingConsent,audit_failures:auditFailures,plan_issues:planIssues,invariant_failures:invariantFailures,duplicate_sessions:duplicates};}
function longFormatRows(manifests=[]){const rows=[];for(const m of manifests){for(const t of m.trials||[]){if(t.is_practice||!t.response)continue;rows.push({study_id:m.study_id,session_id:m.session_id,participant_id:m.participant_id,stimulus_key:t.stimulus_key,condition:m.setup?.altered_condition||m.plan?.design?.altered_condition||'unknown',sequence_index:t.sequence_index,correct:t.response.correct?1:0,rt_ms:t.response.rt_ms,answer:t.response.answer,correct_answer:t.correct_answer,included_by_policy:(m.exclusion_certificate?.trial_certificates||[]).find(x=>x.sequence_index===t.sequence_index)?.included??true,plan_fingerprint:m.plan_fingerprint?.value||''});}}return rows;}
function rowsToCsv(rows){if(!rows.length)return'';const h=Object.keys(rows[0]);return[h,...rows.map(r=>h.map(k=>r[k]??''))].map(row=>row.map(v=>`"${String(v).replaceAll('"','""')}"`).join(',')).join('\n');}
const R_ANALYSIS_SCRIPT=`# FARHP WebLab v0.8 logistic mixed-effects template\n# install.packages(c("readr","lme4","broom.mixed"))\nlibrary(readr)\nlibrary(lme4)\nlibrary(broom.mixed)\nd <- read_csv("farhp_analysis_long_v0.8.csv")\nd <- subset(d, included_by_policy == TRUE)\nd$participant_id <- factor(d$participant_id)\nd$stimulus_key <- factor(d$stimulus_key)\nd$condition <- factor(d$condition)\nmodel <- glmer(correct ~ condition + (1|participant_id) + (1|stimulus_key), data=d, family=binomial)\nprint(summary(model))\nwrite.csv(tidy(model, effects="fixed", conf.int=TRUE), "farhp_glmm_fixed_effects.csv", row.names=FALSE)\n`;
const PY_ANALYSIS_SCRIPT=`# FARHP WebLab v0.8 analysis template\n# pip install pandas statsmodels\nimport pandas as pd\nimport statsmodels.formula.api as smf\ndf = pd.read_csv("farhp_analysis_long_v0.8.csv")\ndf = df[df["included_by_policy"].astype(str).str.lower().isin(["true","1"])]\n# GEE gives population-average inference with participant clustering.\nmodel = smf.gee("correct ~ C(condition)", groups="participant_id", data=df, family=__import__("statsmodels.api").api.families.Binomial()).fit()\nprint(model.summary())\nmodel.summary2().tables[1].to_csv("farhp_gee_results.csv")\n# For confirmatory crossed participant/stimulus random effects, use the included R/lme4 template or a preregistered Bayesian model.\n`;
const oldRenderGroupAnalysisV08=renderGroupAnalysis;renderGroupAnalysis=function(){oldRenderGroupAnalysisV08();const g=experimentState.groupAnalysis;if(!g)return;const q=qualityReviewManifests(experimentState.groupManifests||[]);g.governance_quality=q;$('#groupGovernanceQuality').textContent=q.pass?'PASS':`${q.missing_consent+q.plan_issues+q.invariant_failures} issues`;$('#groupAuditFailures').textContent=q.audit_failures;$('#analysisLongCsvBtn').disabled=!g.source_files;$('#analysisScriptsBtn').disabled=!g.source_files;};
const oldUpdateExperimentUIV08=updateExperimentUI;updateExperimentUI=function(){oldUpdateExperimentUIV08();renderGovernanceUI();};
const oldInitExperimentLabV08=initExperimentLab;initExperimentLab=function(){oldInitExperimentLabV08();$('#roleView').addEventListener('change',e=>applyRoleView(e.target.value));$('#generateWithdrawalBtn').addEventListener('click',()=>{$('#withdrawalCode').value=makeWithdrawalCode();renderGovernanceUI();});$('#consentAttest').addEventListener('change',renderGovernanceUI);$('#eligibilityAttest').addEventListener('change',renderGovernanceUI);$('#verifyAuditBtn').addEventListener('click',renderGovernanceUI);$('#exportAuditBtn').addEventListener('click',async()=>{try{const a=await sealAuditArchive();objectUrlDownload(new Blob([JSON.stringify(a,null,2)],{type:'application/json'}),'farhp_audit_archive_v0.8.json');}catch(e){toast(e.message);}});$('#exportDeidentifiedBtn').addEventListener('click',async()=>{const m=await deidentifiedStudyManifest();if(m)objectUrlDownload(new Blob([JSON.stringify(m,null,2)],{type:'application/json'}),'farhp_study_deidentified_v0.8.json');});$('#analysisLongCsvBtn').addEventListener('click',()=>{const rows=longFormatRows(experimentState.groupManifests||[]);objectUrlDownload(new Blob([rowsToCsv(rows)],{type:'text/csv;charset=utf-8'}),'farhp_analysis_long_v0.8.csv');});$('#analysisScriptsBtn').addEventListener('click',()=>{objectUrlDownload(new Blob([R_ANALYSIS_SCRIPT],{type:'text/plain;charset=utf-8'}),'farhp_glmm_template_v0.8.R');setTimeout(()=>objectUrlDownload(new Blob([PY_ANALYSIS_SCRIPT],{type:'text/plain;charset=utf-8'}),'farhp_gee_template_v0.8.py'),120);});applyRoleView('researcher');renderGovernanceUI();};
const oldImportGroupFilesV08=importGroupFiles;importGroupFiles=async function(){const files=[...$('#groupJsonInput').files];const manifests=[];for(const f of files){try{manifests.push(JSON.parse(await f.text()));}catch(e){console.warn('invalid JSON',f.name,e);}}experimentState.groupManifests=manifests;experimentState.groupAnalysis=mergeStudyManifests(manifests);renderGroupAnalysis();};

function bindControls() {
  const rangeMap = [
    ['#f0', 'f0', Number], ['#duration', 'duration', Number], ['#anchor', 'anchor', Number], ['#gain', 'gain', Number], ['#strength', 'strength', Number],
  ];
  for (const [sel, key, parse] of rangeMap) $(sel).addEventListener('input', e => {
    state[key] = parse(e.target.value);
    if (key === 'f0') state.amplitudes = makeAmplitudes(state.vowel, state.K, state.f0);
    if (key === 'strength') state.phase = state.targetPhase.map((v, i) => geodesicInterpolate(state.basePhase[i], v, state.strength));
    updateAll();
  });
  $('#harmonics').addEventListener('input', e => { state.K = Number(e.target.value); rebuildModel({ preserveCustom: state.phasePreset === 'custom' }); });
  $('#vowelPreset').addEventListener('change', e => { state.vowel = e.target.value; state.amplitudes = makeAmplitudes(state.vowel, state.K, state.f0); updateAll(); });
  $('#phasePreset').addEventListener('change', e => { state.phasePreset = e.target.value; state.targetPhase = phasePreset(state.phasePreset, state.K); state.phase = state.targetPhase.map((v, i) => geodesicInterpolate(0, v, state.strength)); updateAll(); });
  $('#quantization').addEventListener('change', e => { state.quantM = Number(e.target.value); updateAll(); });
  $('#playBtn').addEventListener('click', playAudio); $('#stopBtn').addEventListener('click', stopAudio);
  $('#resetBtn').addEventListener('click', () => { Object.assign(state, { f0:125, duration:.8, K:24, anchor:.35, gain:.8, vowel:'a', phasePreset:'curved', strength:1, quantM:16 }); syncControls(); rebuildModel(); toast('已重設'); });
  $('#normalizeAmpBtn').addEventListener('click', () => { const m = Math.max(...state.amplitudes, 1e-9); state.amplitudes = state.amplitudes.map(v => v / m); updateAll(); });
  $('#wavBtn').addEventListener('click', () => objectUrlDownload(encodeWav(synthesize().samples, SAMPLE_RATE), `farhp_${Math.round(state.f0)}Hz.wav`));
  $('#jsonBtn').addEventListener('click', () => objectUrlDownload(new Blob([JSON.stringify(specObject(), null, 2)], { type:'application/json' }), 'farhp_frame.json'));
  $('#jsonInput').addEventListener('change', async e => { try { loadSpec(JSON.parse(await e.target.files[0].text())); toast('JSON 已載入'); } catch (err) { toast(`JSON 載入失敗：${err.message}`); } e.target.value=''; });
  $('#shift').addEventListener('input', e => { $('#shiftOut').value = `${fmt(Number(e.target.value), 2)} ms`; });
  $('#runShiftTest').addEventListener('click', () => runShiftTest()); $('#runQuantTest').addEventListener('click', () => runQuantTest());
  $('#captureBaseline').addEventListener('click', captureBaseline); $('#runInvariantTest').addEventListener('click', runInvariantTest);
  $('#chooseWavBtn').addEventListener('click', () => $('#wavInput').click()); $('#wavInput').addEventListener('change', e => e.target.files[0] && analyzeWavFile(e.target.files[0]));
  const drop = $('#wavDrop');
  ['dragenter','dragover'].forEach(n => drop.addEventListener(n, e => { e.preventDefault(); drop.classList.add('dragging'); }));
  ['dragleave','drop'].forEach(n => drop.addEventListener(n, e => { e.preventDefault(); drop.classList.remove('dragging'); }));
  drop.addEventListener('drop', e => { const f = e.dataTransfer.files[0]; if (f) analyzeWavFile(f); });
  $('#useAnalysisBtn').addEventListener('click', () => {
    const a = state.analysis; state.f0 = a.f0; state.K = a.amplitudes.length; state.duration = .8; state.anchor = a.anchor; state.vowel = 'flat'; state.phasePreset = 'custom'; state.strength = 1; state.quantM = 0;
    state.amplitudes = a.amplitudes.slice(); state.phase = a.farhp.slice(); state.basePhase = new Array(state.K).fill(0); state.targetPhase = state.phase.slice(); syncControls(); updateAll();
    location.hash = '#lab'; toast('分析結果已載入合成實驗台');
  });
  $('#analysisJsonBtn').addEventListener('click', () => objectUrlDownload(new Blob([JSON.stringify(analysisSpec(), null, 2)], { type:'application/json' }), 'farhp_analysis.json'));
  $('#themeToggle').addEventListener('click', () => { const root = document.documentElement; root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light'; localStorage.setItem('farhp-theme', root.dataset.theme); updateVisualsOnly(); });
  window.addEventListener('resize', () => { drawWave(); drawSpectrum(); drawPhaseWheel(); drawToneContour(); drawSyllableWave(); drawUtteranceF0(); drawUtteranceWave(); });
}

function init() {
  document.documentElement.dataset.theme = localStorage.getItem('farhp-theme') || 'dark';
  bindControls(); syncControls(); rebuildModel(); initSyllableComposer(); initUtteranceComposer(); initExperimentLab(); drawHero(); runShiftTest(false); captureBaseline();
}

document.addEventListener('DOMContentLoaded', init);
