# Axioglyph FARHP Audio Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore browser FARHP phase-sound synthesis inside Axioglyph with three synthetic voice profiles, current/automatic/random playback, replayable seeds, stop control, and WAV export.

**Architecture:** Add one DOM-independent UMD audio module derived from the current WebLab synthesis path, then let the existing Axioglyph controller map validated recipes into that module. Keep PH16 synthesis explicitly representative, reject unsupported FARHP-G/silent/invalid cases, and package the new runtime file through the existing bounded Worker build.

**Tech Stack:** Browser JavaScript, Web Audio API, Canvas 2D, Node assertions, Python Playwright, Cloudflare Workers Static Assets.

**Spec:** `docs/superpowers/specs/2026-08-22-axioglyph-farhp-audio-demo-design.md`

## Global Constraints

- No playback before an explicit user gesture.
- PH16 is a visible P1 signature; generated vectors are representative, not unique pronunciation data.
- FARHP-G without inverse-filtering metadata, silent/NONE/boundary recipes, and FAIL recipes are rejected.
- Voice labels are synthetic presets: neutral, male low-range, female high-range; they do not classify physiology or identity.
- Existing EMPSL validation, SVG/JSON export, recipe hashing, and Lab controls remain compatible.
- Auto demo must restore the user's recipe and voice; stop/new playback must cancel any running sequence.
- Random demo displays a seed and replay reconstructs the same recipe, voice, phase, and samples.
- Public assets remain bounded through `site/build.py`.

---

### Task 1: Implement the deterministic FARHP audio kernel

**Files:**
- Create: `empsl/v0.4/assets/farhp_audio.js`
- Create: `empsl/v0.4/tests/test_farhp_audio_v0.4.js`

**Interfaces:**
- Consumes: an EMPSL v0.4 recipe object.
- Produces: `voiceProfiles`, `phaseSignatureVector`, `recipeToPlan`, `synthesize`, `encodeWav`, `seededRandom`, and `createPlayer` under CommonJS and `window.FARHPAudio`.

- [ ] **Step 1: Write the pure-module tests first**

Load one legal example and assert:

```javascript
const A = require('../assets/farhp_audio.js');
const plan = A.recipeToPlan(legal, 'neutral');
assert.equal(plan.playable, true);
assert.equal(plan.onset.symbol, 'ㄍ');
assert.deepEqual(plan.vowelPath, ['u', 'a']);
assert.equal(plan.tone, 1);

for (let index = 0; index < 16; index++) {
  const vector = A.phaseSignatureVector(`PH16-${String(index).padStart(2, '0')}`, 24);
  assert.equal(A.phaseBin(vector), index);
}

const male = A.synthesize(legal, {voice:'male', seed:7});
const neutral = A.synthesize(legal, {voice:'neutral', seed:7});
const female = A.synthesize(legal, {voice:'female', seed:7});
assert(male.meta.base_f0_hz < neutral.meta.base_f0_hz);
assert(neutral.meta.base_f0_hz < female.meta.base_f0_hz);
assert.notDeepEqual([...male.samples.slice(0, 256)], [...female.samples.slice(0, 256)]);
assert.deepEqual(
  [...neutral.samples],
  [...A.synthesize(legal, {voice:'neutral', seed:7}).samples]
);
assert(Math.max(...neutral.samples.map(Math.abs)) <= 0.720001);
```

Also assert invalid, silent/NONE, and FARHP-G recipes return `playable:false`; phase changes alter samples while preserving duration/base F0; WAV bytes start with `RIFF` and contain `WAVE`.

- [ ] **Step 2: Run the test and confirm the module-missing failure**

Run: `node tests/test_farhp_audio_v0.4.js`

Expected: FAIL because `assets/farhp_audio.js` does not exist.

- [ ] **Step 3: Implement the UMD kernel**

Use a factory wrapper and expose:

```javascript
(function(root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FARHPAudio = factory();
})(typeof self !== 'undefined' ? self : this, function() {
  // constants, mappings, synthesis, WAV and player
  return {voiceProfiles, phaseSignatureVector, phaseBin, recipeToPlan,
    synthesize, encodeWav, seededRandom, createPlayer};
});
```

Port the harmonic/formant/tone/onset/coda equations from the current WebLab path, using the exact voice values and rejection rules in the spec. `createPlayer()` owns one AudioContext and source; `unlock()` creates/resumes it, `play()` returns a promise resolved by `onended`, and `stop()` resolves an interrupted play without throwing.

- [ ] **Step 4: Run numerical and syntax verification**

```powershell
node tests/test_farhp_audio_v0.4.js
node --check assets/farhp_audio.js
```

- [ ] **Step 5: Commit the audio kernel**

```powershell
git add -- empsl/v0.4/assets/farhp_audio.js empsl/v0.4/tests/test_farhp_audio_v0.4.js
git commit -m "feat: add deterministic FARHP browser audio kernel"
```

---

### Task 2: Add the accessible sound studio UI

**Files:**
- Modify: `empsl/v0.4/index.html`
- Modify: `empsl/v0.4/assets/site.css`
- Modify: `empsl/v0.4/tests/test_site_content_v0.4.py`

**Interfaces:**
- Consumes: existing `#lab`, recipe controls, and `assets/farhp_audio.js`.
- Produces: `#soundStudio`, `#soundStatus`, voice buttons, playback/demo/export buttons, metadata fields, and `#soundWaveCanvas`.

- [ ] **Step 1: Add the structural contract before HTML**

Require these IDs:

```python
REQUIRED_SOUND_IDS = {
    "soundStudio", "soundStatus", "playSound", "stopSound", "exportSoundWav",
    "autoSoundDemo", "randomSoundDemo", "replayRandomSound", "soundWaveCanvas",
    "soundReading", "soundVoice", "soundPhase", "soundDomain", "soundSeed",
}
```

Assert three `data-voice` buttons exist, the disclaimer contains `合成聲線，不代表生理分類`, the page contains `PH16 代表性合成`, and the audio script appears before `assets/app.js`.

- [ ] **Step 2: Run the site contract and observe missing UI failures**

Run: `python -B tests/test_site_content_v0.4.py -v`

- [ ] **Step 3: Add the sound studio markup**

Place the section after `.lab-workspace` and before `#evidence`. Use buttons with `type=button`; voice buttons use `aria-pressed`; status uses `role=status aria-live=polite`; canvas has a descriptive label. Add:

```html
<script src="assets/farhp_audio.js?v=20260822"></script>
```

before the versioned application controller.

- [ ] **Step 4: Style desktop, mobile, selected, playing, and disabled states**

Use the existing copper/signal palette, a two-column control/wave layout on desktop, one column under 820px, visible keyboard focus, and no animation requirement for understanding state.

- [ ] **Step 5: Verify and commit the UI shell**

```powershell
python -B tests/test_site_content_v0.4.py -v
git diff --check
git add -- empsl/v0.4/index.html empsl/v0.4/assets/site.css empsl/v0.4/tests/test_site_content_v0.4.py
git commit -m "feat: add the Axioglyph sound studio UI"
```

---

### Task 3: Connect playback, automatic demo, and seeded random demo

**Files:**
- Modify: `empsl/v0.4/assets/app.js`
- Modify: `empsl/v0.4/tests/test_browser_v0.4.py`

**Interfaces:**
- Consumes: `window.FARHPAudio`, the current recipe, existing `setUI()`, examples, and the Task 2 DOM IDs.
- Produces: current playback, stop, WAV export, voice selection, three-step auto demo, seeded random/replay, waveform rendering, and rejection messaging.

- [ ] **Step 1: Extend the real HTTP browser test first**

Add checks:

```python
assert page.locator('#soundStatus').inner_text().startswith('可以播放')
page.click('[data-voice="male"]')
assert page.locator('[data-voice="male"]').get_attribute('aria-pressed') == 'true'
page.click('#playSound')
page.wait_for_function("document.querySelector('#soundStatus').textContent.includes('播放')")

page.click('#autoSoundDemo')
page.wait_for_function("document.querySelector('#soundStatus').textContent.includes('自動示範完成')", timeout=10_000)

page.click('#randomSoundDemo')
page.wait_for_function("document.querySelector('#soundSeed').textContent !== '—'", timeout=5_000)
seed = page.locator('#soundSeed').inner_text()
page.click('#replayRandomSound')
assert page.locator('#soundSeed').inner_text() == seed

with page.expect_download() as wav:
    page.click('#exportSoundWav')
assert wav.value.suggested_filename.startswith('axioglyph_')
assert wav.value.suggested_filename.endswith('.wav')
```

Retain every old assertion.

- [ ] **Step 2: Run and confirm controls are inert**

Run: `.\.venv\Scripts\python.exe -B tests/test_browser_v0.4.py`

Expected: FAIL because the controller has no audio listeners or status rendering.

- [ ] **Step 3: Implement playback state and current-sound rendering**

Create one player, selected voice, demo token, and last random seed. Call `player.unlock()` immediately inside click handlers before awaiting recipe hashing. `refreshSoundStudio()` derives a plan after every recipe update, sets status/metadata/button disabled states, and draws the current synthesized waveform without playing.

- [ ] **Step 4: Implement cancel-safe demo workflows**

`runAutoDemo()` saves and restores recipe/voice in `finally`, increments a cancellation token, and plays neutral/current, male/+5 PH16, female/+10 PH16 with 180 ms gaps. `runRandomDemo(seed?)` uses `seededRandom`, filters examples with `recipeToPlan(...).playable`, synchronizes visible/acoustic PH16, stores seed, updates UI, and plays once. Stop increments the token and calls `player.stop()`.

- [ ] **Step 5: Implement WAV export and failure reporting**

Use the existing download helper with a Blob made from `encodeWav()`. Filenames contain recipe ID-safe local text and voice key. Catch audio initialization/playback errors and report them in `soundStatus`; no success message appears before playback actually starts.

- [ ] **Step 6: Run all interaction tests and commit**

```powershell
node tests/test_farhp_audio_v0.4.js
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
.\.venv\Scripts\python.exe -B tests/test_browser_v0.4.py
git diff --check
git add -- empsl/v0.4/assets/app.js empsl/v0.4/tests/test_browser_v0.4.py
git commit -m "feat: connect Axioglyph audio demonstrations"
```

---

### Task 4: Package, document, publish, and verify

**Files:**
- Modify: `site/build.py`
- Modify: `tests/test_axioglyph_bundle.py`
- Modify: `site/llms.txt`
- Modify: `empsl/v0.4/README.md`
- Modify: `empsl/v0.4/index.html` asset version queries

**Interfaces:**
- Consumes: completed audio module/UI/controller.
- Produces: bounded Worker bundle with the audio runtime and a verified live release.

- [ ] **Step 1: Update the bundle contract first**

Add `assets/farhp_audio.js` to the exact required set and assert `llms.txt` mentions browser audio, three voice presets, PH16 representative synthesis, no upload, and no natural-speech claim.

- [ ] **Step 2: Run and confirm the bundle omits audio**

Run: `python -B tests/test_axioglyph_bundle.py -v`

- [ ] **Step 3: Add audio to the public builder and documentation**

Copy the new module, update `llms.txt` and README, and bump changed `site.css`, `app.js`, and audio script queries to a new cache-busting value.

- [ ] **Step 4: Run complete local verification**

```powershell
python -B tests/test_axioglyph_bundle.py -v
python -B empsl/v0.4/tests/test_site_content_v0.4.py -v
node empsl/v0.4/tests/test_farhp_audio_v0.4.js
node empsl/v0.4/tests/test_core_v0.4.js
python -B empsl/v0.4/tools/empsl_v04_batch_check.py
empsl\v0.4\.venv\Scripts\python.exe -B empsl/v0.4/tests/test_browser_v0.4.py
$wr='D:\Ai\網站群\neok-evemisslab-source\node_modules\.bin\wrangler.cmd'
& $wr deploy --dry-run -c wrangler.jsonc
git diff --check
```

- [ ] **Step 5: Commit, push, and deploy the existing Worker**

```powershell
git add -- site tests/test_axioglyph_bundle.py empsl/v0.4/index.html empsl/v0.4/README.md
git commit -m "deploy: publish Axioglyph FARHP audio demos"
git push origin main
python -B site/build.py
$wr='D:\Ai\網站群\neok-evemisslab-source\node_modules\.bin\wrangler.cmd'
& $wr deploy -c wrangler.jsonc
```

- [ ] **Step 6: Verify the public experience**

Use cache-busted HTTP and a real browser. Require HTTP 200 for page/module, 404 for a missing path, exact new asset query, zero console errors, current playback status, voice switch, auto completion, random seed/replay, WAV download, and clean synchronized `main`/`origin/main`.
