(function(root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FARHPAudio = factory();
})(typeof self !== 'undefined' ? self : this, function() {
  'use strict';

  const TAU = Math.PI * 2;
  const SAMPLE_RATE = 24000;
  const HARMONIC_COUNT = 24;
  const PEAK_TARGET = 0.72;

  const voiceProfiles = Object.freeze({
    neutral: Object.freeze({
      key: 'neutral', label: '中性聲', baseF0Hz: 132, formantScale: 1.00,
      spectralTilt: 0.86
    }),
    male: Object.freeze({
      key: 'male', label: '男聲（低域合成）', baseF0Hz: 108, formantScale: 0.90,
      spectralTilt: 0.82
    }),
    female: Object.freeze({
      key: 'female', label: '女聲（高域合成）', baseF0Hz: 205, formantScale: 1.10,
      spectralTilt: 0.94
    })
  });

  const FORMANTS = Object.freeze({
    a: [[730, 100, 1.00], [1090, 140, 0.75], [2440, 180, 0.45]],
    i: [[270, 80, 1.00], [2290, 120, 0.80], [3010, 160, 0.35]],
    u: [[300, 90, 1.00], [870, 110, 0.75], [2240, 170, 0.35]],
    e: [[530, 90, 1.00], [1840, 130, 0.75], [2480, 170, 0.40]],
    o: [[570, 100, 1.00], [840, 120, 0.80], [2410, 180, 0.35]],
    y: [[310, 85, 1.00], [1750, 125, 0.78], [2450, 170, 0.36]],
    er: [[490, 100, 1.00], [1350, 150, 0.68], [1690, 190, 0.48]]
  });

  const ONSETS = Object.freeze({
    'ONSET-B': {symbol:'ㄅ', type:'stop_unasp'},
    'ONSET-P': {symbol:'ㄆ', type:'stop_asp'},
    'ONSET-M': {symbol:'ㄇ', type:'nasal'},
    'ONSET-F': {symbol:'ㄈ', type:'fricative'},
    'ONSET-D': {symbol:'ㄉ', type:'stop_unasp'},
    'ONSET-T': {symbol:'ㄊ', type:'stop_asp'},
    'ONSET-N': {symbol:'ㄋ', type:'nasal'},
    'ONSET-L': {symbol:'ㄌ', type:'lateral'},
    'ONSET-G': {symbol:'ㄍ', type:'stop_unasp'},
    'ONSET-K': {symbol:'ㄎ', type:'stop_asp'},
    'ONSET-H': {symbol:'ㄏ', type:'fricative'},
    'ONSET-J': {symbol:'ㄐ', type:'affricate_unasp'},
    'ONSET-Q': {symbol:'ㄑ', type:'affricate_asp'},
    'ONSET-X': {symbol:'ㄒ', type:'fricative'},
    'ONSET-ZH': {symbol:'ㄓ', type:'affricate_unasp'},
    'ONSET-CH': {symbol:'ㄔ', type:'affricate_asp'},
    'ONSET-SH': {symbol:'ㄕ', type:'fricative'},
    'ONSET-R': {symbol:'ㄖ', type:'approximant'},
    'ONSET-Z': {symbol:'ㄗ', type:'affricate_unasp'},
    'ONSET-C': {symbol:'ㄘ', type:'affricate_asp'},
    'ONSET-S': {symbol:'ㄙ', type:'fricative'}
  });

  const RIMES = Object.freeze({
    'RIME-A': {path:['a'], coda:'none'},
    'RIME-O': {path:['o'], coda:'none'},
    'RIME-E': {path:['e'], coda:'none'},
    'RIME-AI': {path:['a','i'], coda:'none'},
    'RIME-EI': {path:['e','i'], coda:'none'},
    'RIME-AO': {path:['a','o'], coda:'none'},
    'RIME-OU': {path:['o','u'], coda:'none'},
    'RIME-AN': {path:['a'], coda:'n'},
    'RIME-EN': {path:['e'], coda:'n'},
    'RIME-ANG': {path:['a'], coda:'ng'},
    'RIME-ENG': {path:['e'], coda:'ng'},
    'RIME-ER': {path:['er'], coda:'rhotic'}
  });

  const MEDIALS = Object.freeze({
    'HU-KAIKOU': null,
    'HU-QICHI': 'i',
    'HU-HEKOU': 'u',
    'HU-CUOKOU': 'y'
  });

  const MEDIAL_SYMBOLS = Object.freeze({
    'HU-KAIKOU':'', 'HU-QICHI':'ㄧ', 'HU-HEKOU':'ㄨ', 'HU-CUOKOU':'ㄩ'
  });

  const RIME_SYMBOLS = Object.freeze({
    'RIME-A':'ㄚ', 'RIME-O':'ㄛ', 'RIME-E':'ㄜ', 'RIME-AI':'ㄞ',
    'RIME-EI':'ㄟ', 'RIME-AO':'ㄠ', 'RIME-OU':'ㄡ', 'RIME-AN':'ㄢ',
    'RIME-EN':'ㄣ', 'RIME-ANG':'ㄤ', 'RIME-ENG':'ㄥ', 'RIME-ER':'ㄦ'
  });

  const TONES = Object.freeze({T0:0, T1:1, T2:2, T3:3, T4:4});

  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
  const wrapPhase = value => ((value + Math.PI) % TAU + TAU) % TAU - Math.PI;
  const smooth01 = value => {
    const x = clamp(value, 0, 1);
    return x * x * (3 - 2 * x);
  };

  function seededRandom(seed) {
    let value = Number(seed) >>> 0;
    return function random() {
      let t = value += 0x6D2B79F5;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function stringSeed(value) {
    let hash = 0x811c9dc5;
    const text = String(value);
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash >>> 0;
  }

  function phaseIndex(phaseId) {
    const match = /^PH16-(\d{2})$/.exec(String(phaseId || ''));
    if (!match) return null;
    const value = Number(match[1]);
    return value >= 0 && value < 16 ? value : null;
  }

  function phaseCenter(phaseId) {
    const index = phaseIndex(phaseId);
    if (index === null) throw new Error(`unsupported PH16 signature: ${phaseId}`);
    return -Math.PI + (index + 0.5) * TAU / 16;
  }

  function phaseSignatureVector(phaseId, harmonicCount = HARMONIC_COUNT) {
    const count = Math.max(2, Math.floor(harmonicCount));
    const center = phaseCenter(phaseId);
    const result = new Array(count).fill(0);
    const nonFundamentalCount = count - 1;
    for (let index = 1; index < count; index += 1) {
      const angle = TAU * (index - 1) / nonFundamentalCount;
      result[index] = wrapPhase(center + 0.28 * Math.sin(angle));
    }
    return result;
  }

  function phaseBin(vector) {
    const values = Array.from(vector || []).slice(1);
    if (!values.length) throw new Error('phase vector has no relative harmonics');
    let x = 0;
    let y = 0;
    for (const value of values) {
      x += Math.cos(value);
      y += Math.sin(value);
    }
    const angle = wrapPhase(Math.atan2(y, x));
    return ((Math.floor(16 * (angle + Math.PI) / TAU) % 16) + 16) % 16;
  }

  function voiceProfile(key) {
    return voiceProfiles[key] || voiceProfiles.neutral;
  }

  function buildVowelPath(huId, rimeId) {
    const rime = RIMES[rimeId];
    if (!rime) return null;
    const path = rime.path.slice();
    const medial = MEDIALS[huId];
    if (medial && path[0] !== medial && path[0] !== 'er') path.unshift(medial);
    if (huId === 'HU-CUOKOU' && rimeId === 'RIME-ENG') return ['y', 'o'];
    if (huId === 'HU-HEKOU' && rimeId === 'RIME-ENG') return ['u', 'o'];
    return path;
  }

  function derivedReading(onset, huId, rimeId, tone) {
    const core = `${onset.symbol}${MEDIAL_SYMBOLS[huId] ?? ''}${RIME_SYMBOLS[rimeId] ?? ''}`;
    if (tone === 0) return `˙${core}`;
    const mark = tone === 2 ? 'ˊ' : tone === 3 ? 'ˇ' : tone === 4 ? 'ˋ' : '';
    return `${core}${mark}`;
  }

  function recipeToPlan(recipe, voiceKey = 'neutral') {
    const voice = voiceProfile(voiceKey);
    if (!recipe || recipe.validation_certificate?.valid === false) {
      return {playable:false, reason:'invalid-recipe', voice};
    }

    const phonology = Array.isArray(recipe.phonology) ? recipe.phonology : [];
    if (recipe.acoustic?.class === 'silent' || recipe.acoustic?.source === 'NONE' || phonology.includes('ST-BOUNDARY')) {
      return {playable:false, reason:'silent', voice};
    }
    if (recipe.acoustic?.source === 'FARHP-G') {
      return {playable:false, reason:'farhp-g-inversion-required', voice};
    }
    if (recipe.acoustic?.source !== 'FARHP-Y') {
      return {playable:false, reason:'unsupported-domain', voice};
    }

    const onsetId = phonology.find(value => value.startsWith('ONSET-')) || null;
    const huId = phonology.find(value => value.startsWith('HU-')) || 'HU-KAIKOU';
    const rimeId = phonology.find(value => value.startsWith('RIME-')) || null;
    const onset = onsetId ? ONSETS[onsetId] : {symbol:'', type:'none'};
    const rime = RIMES[rimeId];
    const vowelPath = buildVowelPath(huId, rimeId);
    const tone = TONES[recipe.tone];
    const phaseId = recipe.phase || recipe.acoustic?.phase_signature;

    if (!rime || !vowelPath) return {playable:false, reason:'missing-rime', voice};
    if (tone === undefined) return {playable:false, reason:'unsupported-tone', voice};
    if (phaseIndex(phaseId) === null) return {playable:false, reason:'unsupported-phase', voice};

    let durationSec = tone === 0 ? 0.5 : 0.72;
    if (phonology.includes('ST-LONG')) durationSec *= 1.34;
    if (phonology.includes('ST-LIGHT')) durationSec = Math.min(durationSec, 0.5);

    return {
      playable:true,
      reason:null,
      id:recipe.id || 'eml.empsl:glyph:draft',
      reading:recipe.reading || derivedReading(onset, huId, rimeId, tone),
      onsetId,
      onset,
      huId,
      rimeId,
      vowelPath,
      coda:rime.coda,
      tone,
      phaseId,
      phaseCenterRad:phaseCenter(phaseId),
      source:'FARHP-Y',
      durationSec,
      voice
    };
  }

  function toneSemitones(tone, progress) {
    const u = clamp(progress, 0, 1);
    if (tone === 1) return 4.2 + 0.12 * Math.sin(Math.PI * u);
    if (tone === 2) return -1.6 + 7.1 * Math.pow(u, 1.18);
    if (tone === 3) {
      if (u < 0.56) return -1.0 - 5.0 * Math.pow(u / 0.56, 0.9);
      return -6.0 + 6.4 * Math.pow((u - 0.56) / 0.44, 1.12);
    }
    if (tone === 4) return 5.2 - 9.4 * Math.pow(u, 0.82);
    return -0.5 - 2.2 * u;
  }

  function toneF0(tone, progress, baseF0Hz) {
    return baseF0Hz * Math.pow(2, toneSemitones(tone, progress) / 12);
  }

  function vowelWeights(path, progress) {
    if (path.length === 1) return [[path[0], 1]];
    const x = smooth01(progress);
    if (path.length === 2) return [[path[0], 1 - x], [path[1], x]];
    if (x < 0.5) {
      const mix = smooth01(x * 2);
      return [[path[0], 1 - mix], [path[1], mix]];
    }
    const mix = smooth01((x - 0.5) * 2);
    return [[path[1], 1 - mix], [path[2], mix]];
  }

  function formantEnvelope(frequency, formants, scale) {
    let envelope = 0.02;
    for (const [baseCenter, baseBandwidth, gain] of formants) {
      const center = baseCenter * scale;
      const sigma = Math.max(baseBandwidth * scale / 2.355, 1);
      envelope += gain * Math.exp(-0.5 * ((frequency - center) / sigma) ** 2);
    }
    return envelope;
  }

  function harmonicAmplitude(plan, harmonic, f0Hz, progress) {
    const frequency = harmonic * f0Hz;
    let envelope = 0;
    for (const [key, weight] of vowelWeights(plan.vowelPath, Math.min(progress / 0.78, 1))) {
      envelope += weight * formantEnvelope(frequency, FORMANTS[key], plan.voice.formantScale);
    }
    let amplitude = envelope / Math.pow(harmonic, plan.voice.spectralTilt);
    const codaMix = smooth01((progress - 0.70) / 0.27);
    if (plan.coda === 'n') {
      amplitude *= (1 - 0.34 * codaMix * (harmonic / 24)) *
        (1 + 0.30 * codaMix * Math.exp(-0.5 * ((frequency - 260) / 230) ** 2));
    }
    if (plan.coda === 'ng') {
      amplitude *= (1 - 0.42 * codaMix * (harmonic / 24)) *
        (1 + 0.38 * codaMix * Math.exp(-0.5 * ((frequency - 320) / 260) ** 2));
    }
    if (plan.coda === 'rhotic') {
      amplitude *= 1 + 0.30 * codaMix * Math.exp(-0.5 * ((frequency - 1550) / 440) ** 2);
    }
    return amplitude;
  }

  function onsetDuration(type) {
    return ({
      none:0, nasal:0.055, lateral:0.050, approximant:0.055,
      stop_unasp:0.060, stop_asp:0.105, affricate_unasp:0.090,
      affricate_asp:0.125, fricative:0.115
    })[type] ?? 0.06;
  }

  function synthesize(recipe, options = {}) {
    const voiceKey = options.voice || 'neutral';
    const plan = recipeToPlan(recipe, voiceKey);
    if (!plan.playable) {
      const error = new Error(`recipe is not playable: ${plan.reason}`);
      error.code = plan.reason;
      throw error;
    }

    const sampleRate = SAMPLE_RATE;
    const seed = options.seed === undefined
      ? stringSeed(`${plan.id}|${plan.phaseId}|${voiceKey}`)
      : Number(options.seed) >>> 0;
    const random = seededRandom(seed + plan.tone * 97 + stringSeed(plan.onset.symbol));
    const count = Math.max(1, Math.round(plan.durationSec * sampleRate));
    const samples = new Float32Array(count);
    const f0Track = new Float32Array(count);
    const relativePhase = phaseSignatureVector(plan.phaseId, HARMONIC_COUNT);
    const onsetSec = Math.min(onsetDuration(plan.onset.type), plan.durationSec * 0.28);
    let theta = 0;
    let previousNoise = 0;
    let rawPeak = 0;

    for (let sampleIndex = 0; sampleIndex < count; sampleIndex += 1) {
      const time = sampleIndex / sampleRate;
      const progress = time / plan.durationSec;
      const voicedProgress = clamp((time - onsetSec) / Math.max(plan.durationSec - onsetSec, 1e-5), 0, 1);
      const smoothOnset = ['none', 'nasal', 'lateral', 'approximant'].includes(plan.onset.type);
      const contourProgress = smoothOnset ? progress : voicedProgress;
      const f0Hz = toneF0(plan.tone, contourProgress, plan.voice.baseF0Hz);
      f0Track[sampleIndex] = f0Hz;
      theta += TAU * f0Hz / sampleRate;

      const stopLike = ['stop_unasp', 'stop_asp', 'affricate_unasp', 'affricate_asp', 'fricative'].includes(plan.onset.type);
      const attack = stopLike ? smooth01((time - onsetSec * 0.72) / 0.035) : smooth01(time / 0.035);
      const release = smooth01((plan.durationSec - time) / 0.045);
      const toneIntensity = plan.tone === 3
        ? 1 - 0.13 * Math.exp(-0.5 * ((contourProgress - 0.56) / 0.18) ** 2)
        : 1;
      const phaseRamp = smooth01((time - onsetSec * 0.45) / Math.max(0.12, plan.durationSec * 0.27));
      let voiced = 0;

      for (let harmonicIndex = 0; harmonicIndex < HARMONIC_COUNT; harmonicIndex += 1) {
        const harmonic = harmonicIndex + 1;
        if (harmonic * f0Hz >= sampleRate / 2) break;
        let amplitude = harmonicAmplitude(plan, harmonic, f0Hz, voicedProgress);
        if (plan.onset.type === 'nasal' && time < onsetSec + 0.035) amplitude *= harmonic <= 4 ? 0.55 : 0.16;
        if (plan.onset.type === 'lateral' && time < onsetSec + 0.025) amplitude *= 0.42 + 0.42 * Math.exp(-harmonic / 5);
        const phase = harmonicIndex === 0 ? 0 : relativePhase[harmonicIndex] * phaseRamp;
        voiced += amplitude * Math.cos(harmonic * theta + harmonic * 0.35 + phase);
      }
      voiced *= attack * release * toneIntensity;

      const white = random() * 2 - 1;
      const highPassNoise = white - previousNoise;
      previousNoise = white;
      let residual = 0;
      if (plan.onset.type === 'stop_unasp' || plan.onset.type === 'stop_asp') {
        const center = onsetSec * 0.48;
        residual += highPassNoise * Math.exp(-0.5 * ((time - center) / 0.0045) ** 2) * 0.95;
      }
      if (plan.onset.type === 'stop_asp') {
        residual += highPassNoise * 0.34 * smooth01((time - onsetSec * 0.35) / 0.012) *
          (1 - smooth01((time - onsetSec) / 0.040));
      }
      if (plan.onset.type === 'affricate_unasp' || plan.onset.type === 'affricate_asp') {
        const center = onsetSec * 0.28;
        residual += highPassNoise * Math.exp(-0.5 * ((time - center) / 0.005) ** 2) * 0.75;
        residual += highPassNoise * 0.30 * smooth01((time - center) / 0.008) *
          (1 - smooth01((time - onsetSec) / 0.028));
      }
      if (plan.onset.type === 'affricate_asp') {
        residual += highPassNoise * 0.24 * smooth01((time - onsetSec * 0.35) / 0.010) *
          (1 - smooth01((time - onsetSec) / 0.052));
      }
      if (plan.onset.type === 'fricative') {
        residual += highPassNoise * 0.33 * (1 - smooth01((time - onsetSec) / 0.030)) * smooth01(time / 0.012);
      }
      const codaMix = smooth01((progress - 0.76) / 0.20);
      if (plan.coda === 'n') residual += 0.055 * codaMix * Math.sin(TAU * 245 * time + 0.35);
      if (plan.coda === 'ng') residual += 0.070 * codaMix * Math.sin(TAU * 310 * time + 0.245);

      const residualStrength = 0.52;
      samples[sampleIndex] = voiced + residualStrength * residual;
      rawPeak = Math.max(rawPeak, Math.abs(samples[sampleIndex]));
    }

    const scale = rawPeak > 1e-9 ? PEAK_TARGET / rawPeak : 1;
    const fadeCount = Math.min(Math.round(0.015 * sampleRate), Math.floor(count / 4));
    let peak = 0;
    for (let sampleIndex = 0; sampleIndex < count; sampleIndex += 1) {
      let fade = 1;
      if (sampleIndex < fadeCount) fade = sampleIndex / Math.max(1, fadeCount);
      else if (sampleIndex >= count - fadeCount) fade = (count - 1 - sampleIndex) / Math.max(1, fadeCount);
      samples[sampleIndex] *= scale * clamp(fade, 0, 1);
      peak = Math.max(peak, Math.abs(samples[sampleIndex]));
    }

    const midpointF0 = toneF0(plan.tone, 0.5, plan.voice.baseF0Hz);
    const harmonicAmplitudes = Array.from({length:HARMONIC_COUNT}, (_, index) =>
      harmonicAmplitude(plan, index + 1, midpointF0, 0.5)
    );

    const meta = {
      voice_key:plan.voice.key,
      voice_label:plan.voice.label,
      base_f0_hz:plan.voice.baseF0Hz,
      f0_min_hz:Math.min(...f0Track),
      f0_max_hz:Math.max(...f0Track),
      formant_scale:plan.voice.formantScale,
      spectral_tilt:plan.voice.spectralTilt,
      harmonic_amplitudes:harmonicAmplitudes,
      phase_signature:plan.phaseId,
      phase_center_rad:plan.phaseCenterRad,
      representative_phase:true,
      domain:'FARHP-Y',
      sample_rate_hz:sampleRate,
      duration_sec:plan.durationSec,
      seed,
      reading:plan.reading,
      onset:plan.onset.symbol,
      vowel_path:plan.vowelPath.slice(),
      coda:plan.coda,
      tone:plan.tone,
      peak,
      raw_peak:rawPeak
    };

    return {samples, sampleRate, meta, plan};
  }

  function encodeWav(samples, sampleRate = SAMPLE_RATE) {
    const output = new Uint8Array(44 + samples.length * 2);
    const view = new DataView(output.buffer);
    const text = (offset, value) => {
      for (let index = 0; index < value.length; index += 1) view.setUint8(offset + index, value.charCodeAt(index));
    };
    text(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    text(8, 'WAVE');
    text(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    text(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    for (let index = 0; index < samples.length; index += 1) {
      const sample = clamp(samples[index], -1, 1);
      view.setInt16(44 + index * 2, sample < 0 ? sample * 32768 : sample * 32767, true);
    }
    return output;
  }

  function createPlayer() {
    let context = null;
    let source = null;
    let settle = null;

    async function unlock() {
      const AudioContextClass = globalThis.AudioContext || globalThis.webkitAudioContext;
      if (!AudioContextClass) {
        const error = new Error('Web Audio API is not available');
        error.code = 'audio-context-unavailable';
        throw error;
      }
      context ??= new AudioContextClass();
      if (context.state === 'suspended') await context.resume();
      return context;
    }

    function stop() {
      if (source) {
        const previous = source;
        source = null;
        try { previous.stop(); } catch (_) {}
        try { previous.disconnect(); } catch (_) {}
      }
      if (settle) {
        const resolve = settle;
        settle = null;
        resolve({ended:false});
      }
    }

    async function play(samples, sampleRate = SAMPLE_RATE, onStarted) {
      stop();
      const audioContext = await unlock();
      const buffer = audioContext.createBuffer(1, samples.length, sampleRate);
      buffer.copyToChannel(samples, 0);
      const nextSource = audioContext.createBufferSource();
      nextSource.buffer = buffer;
      nextSource.connect(audioContext.destination);
      source = nextSource;
      return new Promise(resolve => {
        settle = resolve;
        nextSource.onended = () => {
          if (source === nextSource) source = null;
          if (settle === resolve) settle = null;
          resolve({ended:true});
        };
        nextSource.start();
        if (typeof onStarted === 'function') onStarted();
      });
    }

    return {
      unlock,
      play,
      stop,
      isPlaying:() => Boolean(source),
      contextState:() => context?.state || 'uninitialized'
    };
  }

  return {
    SAMPLE_RATE,
    voiceProfiles,
    phaseSignatureVector,
    phaseBin,
    recipeToPlan,
    synthesize,
    encodeWav,
    seededRandom,
    createPlayer
  };
});
