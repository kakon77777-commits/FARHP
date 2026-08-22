# Axioglyph Subsite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the EMPSL v0.4 entry page as the content-rich, deployment-neutral Axioglyph subsite with a visitor-first introduction, a research path, the complete interactive lab, and unambiguous action feedback.

**Architecture:** Keep `empsl/v0.4` as the single deployable static root and retain its current data registries and validation engine. Move presentation into a semantic HTML shell plus focused `site.css` and `site.js` assets, while `app.js` continues to own lab state and gains accessible action/download reporting.

**Tech Stack:** Static HTML5, CSS, browser JavaScript, existing EMPSL JavaScript registries/core, Python standard-library tests, optional Python Playwright with local Microsoft Edge or Chrome.

**Spec:** `docs/superpowers/specs/2026-08-22-axioglyph-subsite-design.md`

## Global Constraints

- The public brand is exactly `Axioglyph｜理符`; technical lineage is `Built on EMPSL v0.4`.
- Traditional Chinese is the primary language; English is used only for the brand and necessary technical terms.
- Every site asset URL must remain relative so the folder can be served at a path prefix or a subdomain root.
- Existing data under `data/`, `rules/`, `examples/`, and `assets/empsl_core.js` remains authoritative and must not be duplicated.
- No framework, package manager, external font, analytics, account system, API, database, or CMS is added.
- Existing stable IDs, validation rules, corpus data, and v0.4 behavior must remain compatible.
- v0.5 features are described only as roadmap work, never as delivered behavior.

---

### Task 1: Lock the site information architecture with a failing contract test

**Files:**
- Create: `empsl/v0.4/tests/test_site_content_v0.4.py`
- Test: `empsl/v0.4/index.html`

**Interfaces:**
- Consumes: the current static `index.html` and its established Lab element IDs.
- Produces: a zero-dependency test contract for brand copy, required sections, relative resources, accessibility hooks, and preserved Lab controls.

- [ ] **Step 1: Write the failing test**

Create a `unittest` suite using `html.parser.HTMLParser`. Track headings, IDs, anchors, scripts, stylesheets, buttons, `aria-live`, and `role="status"`. Assert the following exact contract:

```python
REQUIRED_SECTIONS = {
    "concept", "system", "lab", "evidence", "method", "roadmap", "faq"
}
REQUIRED_LAB_IDS = {
    "glyph", "variantMeta", "gid", "frame", "seedBase", "seedTransform",
    "onset", "hu", "rime", "structure", "tone", "phase", "operator",
    "semanticKind", "concept", "inputTypes", "outputType", "arityMode",
    "arityValue", "acousticSource", "acousticClass", "phaseSignature",
    "profileId", "confidence", "legalExample", "invalidExample", "repair",
    "exportSvg", "exportJson", "status", "activityStatus", "issues", "json",
    "stats", "variantGallery", "ruleGrid"
}

class SiteContractTests(unittest.TestCase):
    def test_brand_and_dual_entry_exist(self):
        self.assertIn("Axioglyph｜理符", HTML)
        self.assertIn("Built on EMPSL v0.4", HTML)
        self.assertIn('href="#concept"', HTML)
        self.assertIn('href="#lab"', HTML)

    def test_required_sections_and_lab_controls_exist(self):
        self.assertTrue(REQUIRED_SECTIONS <= parser.ids)
        self.assertTrue(REQUIRED_LAB_IDS <= parser.ids)

    def test_resources_are_relative_and_feedback_is_accessible(self):
        for url in parser.resource_urls:
            self.assertFalse(url.startswith("/"), url)
        self.assertGreaterEqual(parser.aria_live_count, 1)
        self.assertGreaterEqual(parser.status_role_count, 1)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -B tests/test_site_content_v0.4.py -v`

Expected: FAIL because the old page lacks the Axioglyph brand, content sections, external `site.css`, and `activityStatus`.

- [ ] **Step 3: Commit the failing contract test**

```powershell
git add -- empsl/v0.4/tests/test_site_content_v0.4.py
git commit -m "test: define Axioglyph site contract"
```

---

### Task 2: Build the Axioglyph visitor and research shell

**Files:**
- Modify: `empsl/v0.4/index.html`
- Create: `empsl/v0.4/assets/site.css`
- Create: `empsl/v0.4/assets/site.js`
- Test: `empsl/v0.4/tests/test_site_content_v0.4.py`

**Interfaces:**
- Consumes: existing global registries loaded from `data/*.js`, `rules/*.js`, and `examples/*.js`.
- Produces: the section anchors `#concept`, `#system`, `#lab`, `#evidence`, `#method`, `#roadmap`, and `#faq`; all existing Lab IDs; `#siteNavToggle` and `#siteNavLinks` for navigation enhancement.

- [ ] **Step 1: Replace the one-line page with semantic content**

Build the document in this order:

```html
<header class="site-header">...</header>
<main>
  <section class="hero" aria-labelledby="hero-title">...</section>
  <section id="concept" class="section section-light">...</section>
  <section id="system" class="section section-dark">...</section>
  <section id="lab" class="section lab-section">...</section>
  <section id="evidence" class="section section-light">...</section>
  <section id="method" class="section section-dark">...</section>
  <section id="roadmap" class="section section-light">...</section>
  <section id="faq" class="section faq-section">...</section>
</main>
<footer class="site-footer">...</footer>
```

Keep every ID used by `assets/app.js`. Use real copy from the design spec, including the 128 atoms, 256 variants, 30 rules, 4,096 cases, Stable ID boundary, Schema/rule-engine distinction, FARHP boundary, and v0.5 roadmap.

- [ ] **Step 2: Add the distinctive responsive visual system**

Define these tokens and apply them across the page:

```css
:root {
  --ink-950: #0a0d12;
  --ink-900: #111721;
  --paper-50: #fffaf0;
  --paper-100: #f3ead8;
  --copper-500: #c77b3c;
  --signal-400: #63d7d1;
  --danger-500: #dc665d;
  --success-500: #52b788;
  --line-dark: rgba(255, 250, 240, 0.16);
  --line-light: rgba(17, 23, 33, 0.17);
}
```

Implement a sticky header, asymmetric hero, six-slot system diagram, numbered concept cards, readable measure, strong keyboard focus, desktop two-column Lab, mobile one-column Lab, and `prefers-reduced-motion` fallback. Avoid external fonts and root-relative URLs.

- [ ] **Step 3: Add progressive enhancement for navigation and reveals**

`assets/site.js` must expose no globals and behave safely without `IntersectionObserver`:

```javascript
(() => {
  const toggle = document.querySelector('#siteNavToggle');
  const links = document.querySelector('#siteNavLinks');
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    links?.toggleAttribute('data-open', !open);
  });
  document.querySelectorAll('#siteNavLinks a').forEach(link => {
    link.addEventListener('click', () => {
      toggle?.setAttribute('aria-expanded', 'false');
      links?.removeAttribute('data-open');
    });
  });
  const nodes = [...document.querySelectorAll('[data-reveal]')];
  if (!('IntersectionObserver' in window)) {
    nodes.forEach(node => node.setAttribute('data-visible', ''));
    return;
  }
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.setAttribute('data-visible', '');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  nodes.forEach(node => observer.observe(node));
})();
```

- [ ] **Step 4: Run the contract and syntax tests**

Run:

```powershell
python -B tests/test_site_content_v0.4.py -v
node --check assets/site.js
node --check assets/app.js
```

Expected: all site contract tests PASS and both JavaScript files parse without output.

- [ ] **Step 5: Commit the site shell**

```powershell
git add -- empsl/v0.4/index.html empsl/v0.4/assets/site.css empsl/v0.4/assets/site.js
git commit -m "feat: build Axioglyph dual-entry subsite"
```

---

### Task 3: Make every Lab action visibly accountable

**Files:**
- Modify: `empsl/v0.4/assets/app.js`
- Modify: `empsl/v0.4/tests/test_browser_v0.4.py`
- Test: `empsl/v0.4/tests/test_site_content_v0.4.py`

**Interfaces:**
- Consumes: `#activityStatus`, `#status`, all existing form controls, and `EMPSLCore`.
- Produces: `announce(message, tone)`, `download(name, text, type) -> boolean`, keyboard-operable variant buttons, and observable export outcomes.

- [ ] **Step 1: Rewrite the browser test around a real local HTTP origin**

Use `ThreadingHTTPServer`, `SimpleHTTPRequestHandler`, and `functools.partial` to serve `ROOT` on an ephemeral localhost port. Select a browser executable in this order: `EMPSL_CHROMIUM_EXECUTABLE`, local Edge, local Chrome, `/usr/bin/chromium`, then Playwright's bundled Chromium. Add assertions:

```python
page.goto(base_url, wait_until="load")
page.wait_for_function("window.EMPSL_V04_READY===true")
assert page.locator("#activityStatus").get_attribute("aria-live") == "polite"

page.click("#invalidExample")
assert page.locator("#status").inner_text().startswith("FAIL")
assert "已載入錯誤案例" in page.locator("#activityStatus").inner_text()

page.click("#repair")
assert page.locator("#status").inner_text().startswith("PASS")
assert "自動修正完成" in page.locator("#activityStatus").inner_text()

with page.expect_download() as svg_download:
    page.click("#exportSvg")
assert svg_download.value.suggested_filename == "EMPSL_glyph_v0.4.svg"
assert "SVG" in page.locator("#activityStatus").inner_text()

with page.expect_download() as json_download:
    page.click("#exportJson")
assert json_download.value.suggested_filename == "EMPSL_recipe_v0.4.json"
assert "JSON" in page.locator("#activityStatus").inner_text()
```

- [ ] **Step 2: Run the interaction test to verify the new assertions fail**

Run inside a local virtual environment with the existing requirements installed:

```powershell
python -B tests/test_browser_v0.4.py
```

Expected: FAIL because the current application does not announce actions and its variant cards lack button state semantics.

- [ ] **Step 3: Implement accessible action reporting and reliable export**

Add focused helpers to `app.js`:

```javascript
function announce(message, tone = 'neutral') {
  const target = $('#activityStatus');
  target.textContent = message;
  target.dataset.tone = tone;
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
    return false;
  }
}
```

Have each button call `announce()` with its case ID and state. Render variants as `<button type="button" class="atom-card">`, set `aria-pressed`, and announce the selected transform. Export handlers announce success only when `download()` returns `true`; otherwise announce that the browser blocked the download.

- [ ] **Step 4: Run all Lab tests**

Run:

```powershell
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
python -B tests/test_browser_v0.4.py
```

Expected: core reports `30 groups`, batch check reports `4096 cases`, browser test reports `rules=30`, `variants=8`, both downloads, and zero console errors.

- [ ] **Step 5: Commit the Lab feedback improvements**

```powershell
git add -- empsl/v0.4/assets/app.js empsl/v0.4/tests/test_browser_v0.4.py
git commit -m "fix: make Axioglyph lab actions observable"
```

---

### Task 4: Document, visually verify, and package the local result

**Files:**
- Modify: `empsl/v0.4/README.md`
- Modify: `empsl/README.md`
- Test: all files changed in Tasks 1–3

**Interfaces:**
- Consumes: the completed static subsite and existing validation commands.
- Produces: exact local-run instructions, deployment-neutral guidance, and final verification evidence.

- [ ] **Step 1: Update the documentation**

Add the public name, current content map, and the supported local command:

```powershell
python -B -m http.server 8765 --bind 127.0.0.1
```

Document `http://127.0.0.1:8765/` as the supported entry. State that the folder can later be mounted under a route prefix or deployed as a subdomain root because all site dependencies are relative.

- [ ] **Step 2: Run the complete automated verification**

```powershell
python -B tests/test_site_content_v0.4.py -v
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
python -B tests/test_browser_v0.4.py
git diff --check
```

Expected: all tests PASS and `git diff --check` prints nothing.

- [ ] **Step 3: Perform real-browser visual QA**

Serve the page over localhost and inspect it at one desktop viewport and one mobile viewport. Verify the hero, both CTAs, all seven section anchors, mobile navigation, Lab initialization, invalid/repair path, R90 selection, SVG download, JSON download, focus visibility, no horizontal overflow, and zero console errors.

- [ ] **Step 4: Review repository scope and commit documentation**

```powershell
git status --short
git diff --stat HEAD~3
git add -- empsl/v0.4/README.md empsl/README.md
git commit -m "docs: document the Axioglyph subsite"
```

Expected: only the design, plan, Axioglyph site, tests, and EMPSL README files are part of the feature history.
