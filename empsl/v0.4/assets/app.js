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

    document.querySelectorAll('.lab-controls select, .lab-controls input').forEach(control => {
      control.addEventListener('input', async () => {
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
      const repaired = EMPSLCore.autoRepair(recipeFromUI(), R, V, T, RC);
      await setUI(repaired);
      announce(`自動修正完成 · ${current.validation_certificate.status}`, current.validation_certificate.valid ? 'success' : 'error');
    });

    $('#legalExample').addEventListener('click', async () => {
      const legal = EX.recipes.filter(recipe => recipe.validation_certificate.valid);
      const recipe = legal[Math.floor(Math.random() * legal.length)];
      await setUI(recipe);
      announce(`已載入合法案例：${recipe.id} · PASS`, 'success');
    });

    $('#invalidExample').addEventListener('click', async () => {
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
