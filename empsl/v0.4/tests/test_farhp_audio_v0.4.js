'use strict';

const assert = require('assert');

global.window = {};
require('../examples/EMPSL_legality_examples_v0.4.js');

const A = require('../assets/farhp_audio.js');
const recipes = window.EMPSL_LEGALITY_EXAMPLES.recipes;
const legal = recipes.find(recipe => recipe.validation_certificate.valid && recipe.id.includes('light'));
const invalid = recipes.find(recipe => !recipe.validation_certificate.valid);

assert(legal, 'expected the legal light example');
assert(invalid, 'expected an invalid example');

const plan = A.recipeToPlan(legal, 'neutral');
assert.equal(plan.playable, true);
assert.equal(plan.onset.symbol, 'ㄍ');
assert.deepEqual(plan.vowelPath, ['u', 'a']);
assert.equal(plan.coda, 'ng');
assert.equal(plan.tone, 1);
assert.equal(plan.voice.key, 'neutral');

const noReading = JSON.parse(JSON.stringify(legal));
noReading.reading = '';
assert.equal(A.recipeToPlan(noReading, 'neutral').reading, 'ㄍㄨㄤ');

for (let index = 0; index < 16; index += 1) {
  const phaseId = `PH16-${String(index).padStart(2, '0')}`;
  const vector = A.phaseSignatureVector(phaseId, 24);
  assert.equal(vector.length, 24);
  assert.equal(vector[0], 0);
  assert.equal(A.phaseBin(vector), index, phaseId);
}

assert.equal(A.voiceProfiles.male.baseF0Hz, 108);
assert.equal(A.voiceProfiles.neutral.baseF0Hz, 132);
assert.equal(A.voiceProfiles.female.baseF0Hz, 205);
assert(A.voiceProfiles.male.formantScale < A.voiceProfiles.neutral.formantScale);
assert(A.voiceProfiles.neutral.formantScale < A.voiceProfiles.female.formantScale);

const male = A.synthesize(legal, { voice: 'male', seed: 7 });
const neutral = A.synthesize(legal, { voice: 'neutral', seed: 7 });
const female = A.synthesize(legal, { voice: 'female', seed: 7 });

assert.equal(male.meta.base_f0_hz, 108);
assert.equal(neutral.meta.base_f0_hz, 132);
assert.equal(female.meta.base_f0_hz, 205);
assert.equal(male.samples.length, neutral.samples.length);
assert.equal(neutral.samples.length, female.samples.length);
let voiceDelta = 0;
for (let index = 0; index < male.samples.length; index += 1) {
  voiceDelta += Math.abs(male.samples[index] - female.samples[index]);
}
assert(voiceDelta > 1, voiceDelta);

const neutralAgain = A.synthesize(legal, { voice: 'neutral', seed: 7 });
assert.deepEqual([...neutral.samples], [...neutralAgain.samples]);

let peak = 0;
for (const sample of neutral.samples) {
  assert(Number.isFinite(sample));
  peak = Math.max(peak, Math.abs(sample));
}
assert(peak <= 0.720001, peak);

const alteredRecipe = JSON.parse(JSON.stringify(legal));
alteredRecipe.phase = 'PH16-11';
alteredRecipe.acoustic.phase_signature = 'PH16-11';
const altered = A.synthesize(alteredRecipe, { voice: 'neutral', seed: 7 });
assert.equal(altered.meta.base_f0_hz, neutral.meta.base_f0_hz);
assert.equal(altered.meta.duration_sec, neutral.meta.duration_sec);
assert.deepEqual(altered.meta.harmonic_amplitudes, neutral.meta.harmonic_amplitudes);
let phaseDelta = 0;
for (let index = 0; index < altered.samples.length; index += 1) {
  phaseDelta += Math.abs(altered.samples[index] - neutral.samples[index]);
}
assert(phaseDelta > 1, phaseDelta);

assert.equal(A.recipeToPlan(invalid, 'neutral').playable, false);

const silent = JSON.parse(JSON.stringify(legal));
silent.validation_certificate = { valid: true, status: 'PASS' };
silent.phonology = ['ST-BOUNDARY'];
silent.acoustic.source = 'NONE';
silent.acoustic.class = 'silent';
assert.equal(A.recipeToPlan(silent, 'neutral').reason, 'silent');

const farhpG = JSON.parse(JSON.stringify(legal));
farhpG.validation_certificate = { valid: true, status: 'PASS' };
farhpG.acoustic.source = 'FARHP-G';
assert.equal(A.recipeToPlan(farhpG, 'neutral').reason, 'farhp-g-inversion-required');

const rngA = A.seededRandom(1234);
const rngB = A.seededRandom(1234);
for (let index = 0; index < 20; index += 1) assert.equal(rngA(), rngB());

const wav = A.encodeWav(neutral.samples, neutral.sampleRate);
const ascii = (start, length) => String.fromCharCode(...wav.slice(start, start + length));
assert.equal(ascii(0, 4), 'RIFF');
assert.equal(ascii(8, 4), 'WAVE');
assert.equal(new DataView(wav.buffer, wav.byteOffset, wav.byteLength).getUint32(24, true), 24000);
assert.equal(wav.length, 44 + neutral.samples.length * 2);

console.log('PASS FARHP audio v0.4 · PH16=16 · voices=3 · deterministic · WAV');
