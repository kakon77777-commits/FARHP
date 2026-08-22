(() => {
  const $ = selector => document.querySelector(selector);
  const activity = $('#activityStatus');

  window.EMPSL_V04_READY = false;

  function announce(message, tone = 'neutral') {
    if (!activity) return;
    activity.textContent = message;
    activity.dataset.tone = tone;
  }

  function failInitialization(error) {
    const status = $('#status');
    if (status) {
      status.textContent = '初始化失敗 · 請確認研究資料是否完整載入';
      status.className = 'validation-status bad';
    }
    announce('實驗室無法啟動；靜態研究內容仍可閱讀。', 'error');
    console.error('EMPSL v0.4 initialization failed', error);
  }

  try {
    const R = window.EMPSL_ATOM_REGISTRY;
    const V = window.EMPSL_SEED_VARIANT_REGISTRY;
    const T = window.EMPSL_GRAMMAR_TABLES;
    const RC = window.EMPSL_RULE_CATALOG;
    const LR = window.EMPSL_LEGALITY_REPORT;
    const EX = window.EMPSL_LEGALITY_EXAMPLES;
    const Audio = window.FARHPAudio;

    if (!R || !V || !T || !RC || !LR || !EX || !window.EMPSLCore) {
      throw new Error('A required EMPSL registry or engine is missing');
    }

    const byId = Object.fromEntries(R.atoms.map(atom => [atom.id, atom]));
    const byVariant = Object.fromEntries(V.variants.map(variant => [variant.id, variant]));
    const byTransform = Object.fromEntries(V.transforms.map(transform => [transform.id, transform]));
    const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[character]);

    function addOptions(select, ids, labeler = id => id, blank = false) {
      select.innerHTML = `${blank ? '<option value="">—</option>' : ''}${ids.map(id => (
        `<option value="${id}">${escapeHtml(labeler(id))}</option>`
      )).join('')}`;
    }

    addOptions($('#frame'), T.frames, id => `${id} · ${byId[id].label}`);
    addOptions($('#seedBase'), T.seeds, id => `${id} · ${byId[id].label}`);
    addOptions($('#seedTransform'), T.trans, id => `${id} · ${byTransform[id].label}`);
    addOptions($('#onset'), T.onsets, id => `${id} · ${byId[id].label}`, true);
    addOptions($('#hu'), T.hus, id => `${id} · ${byId[id].label}`, true);
    addOptions($('#rime'), T.rimes, id => `${id} · ${byId[id].label}`, true);
    addOptions($('#structure'), T.structs, id => `${id} · ${byId[id].label}`, true);
    addOptions($('#tone'), T.tones, id => `${id} · ${byId[id].label}`);
    addOptions($('#phase'), T.phases, id => `${id} · ${byId[id].label}`);
    addOptions($('#operator'), T.ops, id => `${id} · ${byId[id].label}`);
    addOptions($('#transformRole'), T.roles);
    addOptions($('#semanticKind'), T.kinds);
    addOptions($('#outputType'), T.types);
    addOptions($('#acousticSource'), T.sources);
    addOptions($('#acousticClass'), T.classes);
    addOptions($('#phaseSignature'), T.phases);

    let current = structuredClone(EX.recipes.find(recipe => recipe.validation_certificate.valid) || EX.recipes[0]);
    const audioPlayer = Audio?.createPlayer();
    let selectedVoice = 'neutral';
    let activeSoundSeed = null;
    let lastSynthesis = null;
    let lastRandomSeed = null;
    let soundDemoToken = 0;
    let activeDemoRestore = null;

    function variantId() {
      return `${$('#seedBase').value}@${$('#seedTransform').value}`;
    }

    function inputTypes() {
      return $('#inputTypes').value.split(',').map(value => value.trim()).filter(Boolean);
    }

    function recipeFromUI() {
      const mode = $('#arityMode').value;
      const amount = Number($('#arityValue').value || 0);
      const arity = mode === 'fixed'
        ? { mode, value: amount }
        : { mode, min: amount, max: null };

      return {
        id: $('#gid').value || 'eml.empsl:glyph:draft',
        version: '0.4',
        frame: $('#frame').value,
        seed_base: $('#seedBase').value,
        seed_transform: $('#seedTransform').value,
        seed_variant: variantId(),
        phonology: [$('#onset').value, $('#hu').value, $('#rime').value, $('#structure').value].filter(Boolean),
        tone: $('#tone').value,
        phase: $('#phase').value,
        operator: $('#operator').value,
        transform_role: $('#transformRole').value,
        semantic: {
          kind: $('#semanticKind').value,
          concept_id: $('#concept').value,
          signature: {
            inputs: inputTypes(),
            output: $('#outputType').value,
            arity
          }
        },
        acoustic: {
          source: $('#acousticSource').value,
          class: $('#acousticClass').value,
          phase_signature: $('#phaseSignature').value,
          profile_id: $('#profileId').value || null,
          confidence: Number($('#confidence').value)
        },
        reading: $('#reading').value,
        gloss: $('#gloss').value
      };
    }

    async function setUI(recipe) {
      current = structuredClone(recipe);
      $('#gid').value = recipe.id || '';
      $('#frame').value = recipe.frame;
      $('#seedBase').value = recipe.seed_base;
      $('#seedTransform').value = recipe.seed_transform;

      const classified = EMPSLCore.classifyMarks(recipe, R);
      $('#onset').value = classified.onset[0] || '';
      $('#hu').value = classified.four_hu[0] || '';
      $('#rime').value = classified.rime[0] || '';
      $('#structure').value = classified.structure[0] || '';
      $('#tone').value = recipe.tone;
      $('#phase').value = recipe.phase;
      $('#operator').value = recipe.operator;
      $('#transformRole').value = recipe.transform_role;
      $('#semanticKind').value = recipe.semantic.kind;
      $('#concept').value = recipe.semantic.concept_id;
      $('#inputTypes').value = (recipe.semantic.signature.inputs || []).join(', ');
      $('#outputType').value = recipe.semantic.signature.output;
      $('#arityMode').value = recipe.semantic.signature.arity.mode;
      $('#arityValue').value = recipe.semantic.signature.arity.mode === 'fixed'
        ? recipe.semantic.signature.arity.value
        : recipe.semantic.signature.arity.min;
      $('#acousticSource').value = recipe.acoustic.source;
      $('#acousticClass').value = recipe.acoustic.class;
      $('#phaseSignature').value = recipe.acoustic.phase_signature;
      $('#profileId').value = recipe.acoustic.profile_id || '';
      $('#confidence').value = recipe.acoustic.confidence ?? 0.8;
      $('#confidenceValue').textContent = Number($('#confidence').value).toFixed(2);
      $('#reading').value = recipe.reading || '';
      $('#gloss').value = recipe.gloss || '';

      await update();
      renderVariantGallery();
    }

    async function update() {
      const recipe = recipeFromUI();
      const certificate = EMPSLCore.validateRecipeV04(recipe, R, V, T, RC);
      recipe.validation_certificate = certificate;
      recipe.recipe_sha256 = await EMPSLCore.recipeHash(recipe);
      current = recipe;

      $('#glyph').innerHTML = EMPSLCore.composeSvg(recipe, R, V, { rawVariant: $('#rawMode').checked });
      const variant = byVariant[recipe.seed_variant];
      $('#variantMeta').textContent = variant
        ? `${recipe.seed_variant} · ${variant.transform_label} · witness ${variant.witness_bits}`
        : 'unknown variant';

      const status = $('#status');
      status.textContent = certificate.valid
        ? `PASS · ${certificate.warning_count} warning · ${recipe.recipe_sha256.slice(0, 16)}…`
        : `FAIL · ${certificate.error_count} errors · ${certificate.warning_count} warnings`;
      status.className = `validation-status ${certificate.valid ? 'ok' : 'bad'}`;
      status.dataset.state = certificate.status;

      $('#json').textContent = JSON.stringify(recipe, null, 2);
      renderIssues(certificate);
      $('#inferredClass').textContent = EMPSLCore.inferAcousticClass(recipe, R, T);
      refreshSoundStudio();
      return recipe;
    }

    function renderIssues(certificate) {
      if (!certificate.issues.length) {
        $('#issues').innerHTML = '<div class="empty">沒有錯誤或警告。</div>';
        return;
      }

      $('#issues').innerHTML = certificate.issues.map(issue => (
        `<article class="issue ${issue.severity}">` +
          `<b>${issue.rule_id} · ${escapeHtml(issue.message)}</b>` +
          `<span>${escapeHtml(issue.domain)} · ${escapeHtml(issue.field || '—')}</span>` +
          `${issue.suggestion ? `<small>建議：${escapeHtml(issue.suggestion)}</small>` : ''}` +
        '</article>'
      )).join('');
    }

    function renderRules() {
      const domains = {
        glyph: '字形',
        phonology: '音系',
        transform: '變換',
        semantics: '語義',
        acoustics: '聲學'
      };

      $('#ruleGrid').innerHTML = RC.rules.map(rule => (
        '<article class="rule">' +
          `<header><b>${rule.id}</b><span>${domains[rule.domain]} · ${rule.severity}</span></header>` +
          `<h3>${escapeHtml(rule.title)}</h3>` +
          `<p>${escapeHtml(rule.description)}</p>` +
          `<em>${(LR.rule_hit_counts[rule.id] || 0).toLocaleString()} corpus hits</em>` +
        '</article>'
      )).join('');
    }

    function renderStats() {
      const breakdown = LR.generator_breakdown;
      $('#stats').innerHTML =
        `<div class="stat"><b>${RC.rule_count}</b><span>合法性規則</span></div>` +
        `<div class="stat"><b>${LR.sample_count.toLocaleString()}</b><span>驗證語料</span></div>` +
        `<div class="stat"><b>${breakdown.valid.valid.toLocaleString()}</b><span>合法生成 PASS</span></div>` +
        `<div class="stat"><b>${breakdown['mutated-invalid'].invalid.toLocaleString()}</b><span>破壞案例攔截</span></div>` +
        `<div class="stat"><b>${breakdown.fuzz.invalid.toLocaleString()}</b><span>模糊測試攔截</span></div>`;
    }

    function renderVariantGallery() {
      const base = $('#seedBase').value;
      const variants = V.variants.filter(variant => variant.base_seed === base);
      const selected = variantId();

      $('#variantGallery').innerHTML = variants.map(variant => (
        `<button type="button" class="atom-card" data-id="${variant.id}" ` +
          `aria-label="選擇 ${variant.id} ${escapeHtml(variant.transform_label)}" ` +
          `aria-pressed="${variant.id === selected}">` +
          `<span class="atom-svg"><svg viewBox="0 0 256 256" aria-hidden="true">${variant.body}</svg></span>` +
          `<b>${variant.id}</b><span>${escapeHtml(variant.transform_label)}</span>` +
        '</button>'
      )).join('');

      document.querySelectorAll('#variantGallery .atom-card').forEach(card => {
        card.addEventListener('click', async () => {
          await cancelActiveDemo({restore:false});
          activeSoundSeed = null;
          const variant = byVariant[card.dataset.id];
          $('#seedTransform').value = variant.transform_id;
          syncTransformDefaults();
          const recipe = await update();
          renderVariantGallery();
          announce(`已選擇變體 ${variant.id} · ${recipe.validation_certificate.status}`, recipe.validation_certificate.valid ? 'success' : 'error');
        });
      });
    }

    function syncOperatorDefaults() {
      const operator = $('#operator').value;
      const [mode, amount] = T.op_arity[operator] || ['fixed', 0];
      $('#arityMode').value = mode;
      $('#arityValue').value = amount;
      $('#inputTypes').value = Array(amount).fill('Any').join(', ');

      const kinds = T.op_kind[operator] || ['item'];
      if (!kinds.includes($('#semanticKind').value)) $('#semanticKind').value = kinds[0];

      const frames = T.op_frames[operator] || T.frames;
      if (!frames.includes($('#frame').value)) $('#frame').value = frames[0];
      $('#outputType').value = T.frame_out[$('#frame').value] || 'Any';
    }

    function syncTransformDefaults() {
      const transform = $('#seedTransform').value;
      const roles = T.trans_roles[transform] || ['identity'];
      if (!roles.includes($('#transformRole').value)) $('#transformRole').value = roles[0];

      const kinds = T.trans_kinds[transform] || T.kinds;
      if (!kinds.includes($('#semanticKind').value)) $('#semanticKind').value = kinds[0];
    }

    function syncAcoustic() {
      const recipe = recipeFromUI();
      const acousticClass = EMPSLCore.inferAcousticClass(recipe, R, T);
      $('#acousticClass').value = acousticClass;
      $('#phaseSignature').value = $('#phase').value;

      if (acousticClass === 'silent') {
        $('#acousticSource').value = 'NONE';
        $('#profileId').value = '';
        $('#phase').value = 'PH16-00';
        $('#phaseSignature').value = 'PH16-00';
      } else {
        if ($('#acousticSource').value === 'NONE') $('#acousticSource').value = 'FARHP-Y';
        if (!$('#profileId').value) $('#profileId').value = 'eml.farhp:profile:draft';
      }
    }

    function download(name, text, type) {
      let url = '';
      try {
        url = URL.createObjectURL(new Blob([text], { type }));
        const link = document.createElement('a');
        link.href = url;
        link.download = name;
        link.hidden = true;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        return true;
      } catch (error) {
        if (url) URL.revokeObjectURL(url);
        console.error(`Unable to export ${name}`, error);
        return false;
      }
    }

    function soundStatus(message, tone = 'neutral') {
      const target = $('#soundStatus');
      if (!target) return;
      target.textContent = message;
      target.dataset.tone = tone;
    }

    function soundReason(reason) {
      return ({
        'invalid-recipe':'這份配方目前是 FAIL；先修正到 PASS 才能播放。',
        'silent':'這是靜音／邊界配方，所以不會硬塞一個假聲音。',
        'farhp-g-inversion-required':'這份配方是 FARHP-G，但沒有完整逆濾波資料，不能假裝唯一還原。',
        'unsupported-domain':'目前只示範 FARHP-Y 輸出域。',
        'missing-rime':'這份配方沒有可合成的韻類。',
        'unsupported-tone':'目前聲調無法映射到合成器。',
        'unsupported-phase':'目前 PH16 簽名無法映射到代表向量。'
      })[reason] || '這份配方目前無法播放。';
    }

    function setVoiceButtons() {
      document.querySelectorAll('[data-voice]').forEach(button => {
        button.setAttribute('aria-pressed', String(button.dataset.voice === selectedVoice));
      });
    }

    function drawSoundWave(synthesis) {
      const canvas = $('#soundWaveCanvas');
      if (!canvas || !synthesis?.samples?.length) return;
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const width = Math.max(1, Math.round(rect.width * dpr));
      const height = Math.max(1, Math.round(rect.height * dpr));
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }
      const context = canvas.getContext('2d');
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      context.clearRect(0, 0, rect.width, rect.height);
      context.strokeStyle = 'rgba(255,250,240,.12)';
      context.lineWidth = 1;
      for (let row = 1; row < 5; row += 1) {
        const y = rect.height * row / 5;
        context.beginPath(); context.moveTo(0, y); context.lineTo(rect.width, y); context.stroke();
      }
      context.strokeStyle = '#63d7d1';
      context.lineWidth = 1.7;
      context.beginPath();
      const samples = synthesis.samples;
      const step = Math.max(1, Math.floor(samples.length / Math.max(1, rect.width * 2)));
      for (let index = 0; index < samples.length; index += step) {
        const x = index / Math.max(1, samples.length - 1) * rect.width;
        const y = rect.height / 2 - samples[index] / 0.72 * rect.height * 0.42;
        if (index === 0) context.moveTo(x, y);
        else context.lineTo(x, y);
      }
      context.stroke();
      context.fillStyle = 'rgba(255,250,240,.46)';
      context.font = '10px monospace';
      context.fillText(`${synthesis.meta.duration_sec.toFixed(2)} s`, 8, rect.height - 9);
      context.fillText(`${synthesis.meta.f0_min_hz.toFixed(0)}–${synthesis.meta.f0_max_hz.toFixed(0)} Hz`, Math.max(8, rect.width - 112), rect.height - 9);
    }

    function refreshSoundStudio(options = {}) {
      if (!$('#soundStudio')) return;
      setVoiceButtons();
      $('#soundReading').textContent = current.reading || '—';
      $('#soundVoice').textContent = Audio?.voiceProfiles?.[selectedVoice]?.label || '—';
      $('#soundPhase').textContent = current.phase ? `${current.phase} · 代表向量` : '—';
      $('#soundDomain').textContent = current.acoustic?.source || '—';
      $('#soundSeed').textContent = activeSoundSeed === null ? '—' : String(activeSoundSeed >>> 0);

      if (!Audio || !audioPlayer) {
        lastSynthesis = null;
        ['#playSound', '#exportSoundWav', '#autoSoundDemo', '#randomSoundDemo'].forEach(selector => {
          const button = $(selector); if (button) button.disabled = true;
        });
        soundStatus('這個瀏覽器沒有載入 FARHP 音訊模組。', 'error');
        return;
      }

      const plan = Audio.recipeToPlan(current, selectedVoice);
      $('#soundReading').textContent = plan.reading || current.reading || '—';
      $('#playSound').disabled = !plan.playable;
      $('#exportSoundWav').disabled = !plan.playable;
      $('#autoSoundDemo').disabled = false;
      $('#randomSoundDemo').disabled = false;
      $('#replayRandomSound').disabled = lastRandomSeed === null;

      if (!plan.playable) {
        lastSynthesis = null;
        if (!options.keepStatus) soundStatus(soundReason(plan.reason), 'error');
        return;
      }

      try {
        lastSynthesis = Audio.synthesize(current, {
          voice:selectedVoice,
          ...(activeSoundSeed === null ? {} : {seed:activeSoundSeed})
        });
        drawSoundWave(lastSynthesis);
        if (!options.keepStatus) {
          soundStatus(`可以播放：${current.reading || current.id} · ${lastSynthesis.meta.voice_label} · ${current.phase}`, 'ready');
        }
      } catch (error) {
        lastSynthesis = null;
        soundStatus(`合成失敗：${error.message}`, 'error');
      }
    }

    async function playCurrentSound(options = {}) {
      const token = options.token ?? soundDemoToken;
      const plan = Audio?.recipeToPlan(current, selectedVoice);
      if (!plan?.playable) {
        soundStatus(soundReason(plan?.reason), 'error');
        return {ended:false};
      }
      const synthesis = Audio.synthesize(current, {
        voice:selectedVoice,
        ...(activeSoundSeed === null ? {} : {seed:activeSoundSeed})
      });
      lastSynthesis = synthesis;
      drawSoundWave(synthesis);
      try {
        const result = await audioPlayer.play(synthesis.samples, synthesis.sampleRate, () => {
          soundStatus(options.playingMessage || `播放中：${current.reading || current.id} · ${synthesis.meta.voice_label}`, 'playing');
        });
        if (result.ended && token === soundDemoToken && options.completionMessage !== false) {
          soundStatus(options.completionMessage || `播放完成：${current.reading || current.id}`, 'ready');
        }
        return result;
      } catch (error) {
        soundStatus(`播放失敗：${error.message}`, 'error');
        return {ended:false};
      }
    }

    function phaseOffsetRecipe(recipe, offset) {
      const clone = structuredClone(recipe);
      const index = Number(String(clone.phase || 'PH16-00').slice(-2)) || 0;
      const next = `PH16-${String((index + offset + 16) % 16).padStart(2, '0')}`;
      clone.phase = next;
      clone.acoustic.phase_signature = next;
      return clone;
    }

    function playableExamples() {
      return EX.recipes.filter(recipe => recipe.validation_certificate.valid && Audio.recipeToPlan(recipe, 'neutral').playable);
    }

    function randomSeed() {
      if (globalThis.crypto?.getRandomValues) return crypto.getRandomValues(new Uint32Array(1))[0];
      return Date.now() >>> 0;
    }

    const wait = milliseconds => new Promise(resolve => window.setTimeout(resolve, milliseconds));

    async function cancelActiveDemo({restore = true, message = null} = {}) {
      soundDemoToken += 1;
      audioPlayer?.stop();
      const restoreState = activeDemoRestore;
      activeDemoRestore = null;
      if (restore && restoreState) {
        selectedVoice = restoreState.voice;
        activeSoundSeed = restoreState.seed;
        await setUI(restoreState.recipe);
      }
      if (message) soundStatus(message, 'ready');
    }

    async function runAutoDemo() {
      const unlockPromise = audioPlayer.unlock();
      await cancelActiveDemo({restore:true});
      await unlockPromise;
      const candidates = playableExamples();
      const baseSource = Audio.recipeToPlan(current, selectedVoice).playable ? current : candidates[0];
      if (!baseSource) {
        soundStatus('找不到可以自動示範的合法聲音。', 'error');
        return;
      }
      const base = structuredClone(baseSource);
      const token = ++soundDemoToken;
      activeDemoRestore = {token, recipe:structuredClone(current), voice:selectedVoice, seed:activeSoundSeed};
      const steps = [
        {voice:'neutral', offset:0, label:'中性聲'},
        {voice:'male', offset:5, label:'男聲'},
        {voice:'female', offset:10, label:'女聲'}
      ];
      try {
        for (let index = 0; index < steps.length; index += 1) {
          if (token !== soundDemoToken) return;
          const step = steps[index];
          selectedVoice = step.voice;
          activeSoundSeed = (20260822 + index * 65537) >>> 0;
          await setUI(phaseOffsetRecipe(base, step.offset));
          soundStatus(`自動示範 ${index + 1}/${steps.length}：${step.label} · ${current.phase}`, 'playing');
          await playCurrentSound({token, completionMessage:false, playingMessage:`自動示範 ${index + 1}/${steps.length}：${step.label} · ${current.phase}`});
          if (token !== soundDemoToken) return;
          await wait(180);
        }
      } finally {
        if (activeDemoRestore?.token === token) {
          const restoreState = activeDemoRestore;
          activeDemoRestore = null;
          selectedVoice = restoreState.voice;
          activeSoundSeed = restoreState.seed;
          await setUI(restoreState.recipe);
          soundStatus('自動示範完成 · 已還原原本配方', 'ready');
        }
      }
    }

    async function runRandomDemo(seed = randomSeed()) {
      const unlockPromise = audioPlayer.unlock();
      await cancelActiveDemo({restore:true});
      await unlockPromise;
      const candidates = playableExamples();
      if (!candidates.length) {
        soundStatus('找不到可以隨機示範的合法聲音。', 'error');
        return;
      }
      const normalizedSeed = Number(seed) >>> 0;
      const random = Audio.seededRandom(normalizedSeed);
      const recipe = structuredClone(candidates[Math.floor(random() * candidates.length)]);
      const voices = ['neutral', 'male', 'female'];
      selectedVoice = voices[Math.floor(random() * voices.length)];
      const phase = `PH16-${String(Math.floor(random() * 16)).padStart(2, '0')}`;
      recipe.phase = phase;
      recipe.acoustic.phase_signature = phase;
      activeSoundSeed = normalizedSeed;
      lastRandomSeed = normalizedSeed;
      const token = ++soundDemoToken;
      await setUI(recipe);
      $('#replayRandomSound').disabled = false;
      soundStatus(`隨機示範：${recipe.reading || recipe.id} · ${Audio.voiceProfiles[selectedVoice].label} · seed ${normalizedSeed}`, 'playing');
      await playCurrentSound({
        token,
        playingMessage:`隨機示範播放中 · seed ${normalizedSeed}`,
        completionMessage:`隨機示範完成 · seed ${normalizedSeed}`
      });
    }

    document.querySelectorAll('.lab-controls select, .lab-controls input').forEach(control => {
      control.addEventListener('input', async () => {
        await cancelActiveDemo({restore:false});
        activeSoundSeed = null;
        if (control.id === 'operator') syncOperatorDefaults();
        if (control.id === 'seedTransform') syncTransformDefaults();
        if (['onset', 'hu', 'rime', 'structure', 'phase'].includes(control.id)) syncAcoustic();
        if (control.id === 'confidence') $('#confidenceValue').textContent = Number(control.value).toFixed(2);

        const recipe = await update();
        renderVariantGallery();
        announce(`配方已重新驗證 · ${recipe.validation_certificate.status}`, recipe.validation_certificate.valid ? 'success' : 'error');
      });
    });

    $('#repair').addEventListener('click', async () => {
      await cancelActiveDemo({restore:true});
      activeSoundSeed = null;
      const repaired = EMPSLCore.autoRepair(recipeFromUI(), R, V, T, RC);
      await setUI(repaired);
      announce(`自動修正完成 · ${current.validation_certificate.status}`, current.validation_certificate.valid ? 'success' : 'error');
    });

    $('#legalExample').addEventListener('click', async () => {
      await cancelActiveDemo({restore:true});
      activeSoundSeed = null;
      const legal = EX.recipes.filter(recipe => recipe.validation_certificate.valid);
      const recipe = legal[Math.floor(Math.random() * legal.length)];
      await setUI(recipe);
      announce(`已載入合法案例：${recipe.id} · PASS`, 'success');
    });

    $('#invalidExample').addEventListener('click', async () => {
      await cancelActiveDemo({restore:true});
      activeSoundSeed = null;
      const invalid = EX.recipes.filter(recipe => !recipe.validation_certificate.valid);
      const recipe = invalid[Math.floor(Math.random() * invalid.length)];
      await setUI(recipe);
      announce(`已載入錯誤案例：${recipe.id} · FAIL`, 'error');
    });

    $('#exportSvg').addEventListener('click', () => {
      const succeeded = download('EMPSL_glyph_v0.4.svg', EMPSLCore.composeSvg(current, R, V), 'image/svg+xml');
      announce(succeeded ? 'SVG 已匯出。' : 'SVG 匯出被瀏覽器阻擋。', succeeded ? 'success' : 'error');
    });

    $('#exportJson').addEventListener('click', () => {
      const succeeded = download('EMPSL_recipe_v0.4.json', JSON.stringify(current, null, 2), 'application/json');
      announce(succeeded ? 'JSON 配方已匯出。' : 'JSON 匯出被瀏覽器阻擋。', succeeded ? 'success' : 'error');
    });

    document.querySelectorAll('[data-voice]').forEach(button => {
      button.addEventListener('click', async () => {
        await cancelActiveDemo({restore:true});
        selectedVoice = button.dataset.voice;
        activeSoundSeed = null;
        refreshSoundStudio();
      });
    });

    $('#playSound').addEventListener('click', async () => {
      const unlockPromise = audioPlayer.unlock();
      await cancelActiveDemo({restore:true});
      activeSoundSeed = null;
      const token = ++soundDemoToken;
      await unlockPromise;
      refreshSoundStudio({keepStatus:true});
      await playCurrentSound({token});
    });

    $('#stopSound').addEventListener('click', async () => {
      await cancelActiveDemo({restore:true, message:'播放已停止'});
    });

    $('#autoSoundDemo').addEventListener('click', async () => {
      try {
        await runAutoDemo();
      } catch (error) {
        await cancelActiveDemo({restore:true});
        soundStatus(`自動示範失敗：${error.message}`, 'error');
      }
    });

    $('#randomSoundDemo').addEventListener('click', async () => {
      try {
        await runRandomDemo();
      } catch (error) {
        soundStatus(`隨機示範失敗：${error.message}`, 'error');
      }
    });

    $('#replayRandomSound').addEventListener('click', async () => {
      if (lastRandomSeed === null) return;
      try {
        await runRandomDemo(lastRandomSeed);
      } catch (error) {
        soundStatus(`隨機重播失敗：${error.message}`, 'error');
      }
    });

    $('#exportSoundWav').addEventListener('click', () => {
      const plan = Audio?.recipeToPlan(current, selectedVoice);
      if (!plan?.playable) {
        soundStatus(soundReason(plan?.reason), 'error');
        return;
      }
      const synthesis = Audio.synthesize(current, {
        voice:selectedVoice,
        ...(activeSoundSeed === null ? {} : {seed:activeSoundSeed})
      });
      lastSynthesis = synthesis;
      const safeId = String(current.id || 'sound').split(':').at(-1).replace(/[^a-z0-9_-]+/gi, '-');
      const bytes = Audio.encodeWav(synthesis.samples, synthesis.sampleRate);
      const succeeded = download(`axioglyph_${safeId}_${selectedVoice}.wav`, bytes, 'audio/wav');
      soundStatus(succeeded ? `WAV 已匯出 · ${synthesis.meta.voice_label}` : 'WAV 匯出被瀏覽器阻擋。', succeeded ? 'ready' : 'error');
    });

    window.addEventListener('resize', () => {
      if (lastSynthesis) drawSoundWave(lastSynthesis);
    });

    renderStats();
    renderRules();
    setUI(current).then(() => {
      window.EMPSL_V04_READY = true;
      announce('實驗室已就緒 · 初始配方 PASS', 'success');
    }).catch(failInitialization);
  } catch (error) {
    failInitialization(error);
  }
})();
