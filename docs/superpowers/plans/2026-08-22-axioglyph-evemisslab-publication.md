# Axioglyph EveMissLab Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Axioglyph at `axioglyph.evemisslab.com`, rewrite its Chinese introduction in a natural spoken register, and add it to the bilingual `evemisslab.com` index.

**Architecture:** FARHP remains the source repository and produces a curated static bundle served by a Cloudflare assets-only Worker. The separate `evemisslab` repository remains a Cloudflare Pages index and receives one bilingual card after the child site is live.

**Tech Stack:** Static HTML/CSS/JavaScript, Python standard library, Playwright, Cloudflare Workers Static Assets, Wrangler, Cloudflare Pages.

**Spec:** `docs/superpowers/specs/2026-08-22-axioglyph-evemisslab-publication-design.md`

## Global Constraints

- Public URL is exactly `https://axioglyph.evemisslab.com/`.
- Do not modify `D:\Ai\網站群\neok-evemisslab-source`.
- Axioglyph uses an assets-only Worker; the EveMissLab apex remains on its existing Pages project.
- Public bundle includes runtime files only; tests, corpus, tools, specs, archives, and internal Markdown stay private to the source repository.
- Technical field labels and rule names remain precise; visitor-facing Chinese uses short, direct, conversational sentences.
- Deploy the child first, then add and deploy the parent index.
- Do not claim live success until cache-busted public checks confirm the exact new content.

---

### Task 1: Rewrite Axioglyph visitor-facing Chinese

**Files:**
- Modify: `empsl/v0.4/index.html`
- Modify: `empsl/v0.4/tests/test_site_content_v0.4.py`

**Interfaces:**
- Consumes: all current Lab IDs and technical labels.
- Produces: unchanged Lab behavior with a more natural Chinese introduction and canonical production metadata.

- [ ] **Step 1: Tighten the copy contract before changing HTML**

Extend `test_site_content_v0.4.py` to require:

```python
for phrase in (
    "畫一個符號不難。",
    "先不講規格。你只要想一件事。",
    "別只看，直接動手改。",
    "不是「我這邊有跑過」就算數。",
    "現在先把字做好；下一步才是把語言跑起來。",
):
    self.assertIn(phrase, HTML)

for phrase in ("可稽核", "目前權威節點", "形式符號語言工程"):
    self.assertNotIn(phrase, HTML)

self.assertIn('href="https://axioglyph.evemisslab.com/"', HTML)
```

- [ ] **Step 2: Run the contract and observe the expected failure**

Run: `python -B tests/test_site_content_v0.4.py -v`

Expected: FAIL because the old formal copy and missing canonical remain.

- [ ] **Step 3: Rewrite the visitor copy and production metadata**

Update the meta description, Open Graph copy, hero, concept cards, six-slot explanation, Lab introduction, evidence heading, method explanation, roadmap, FAQ, and footer. Preserve every input label, ID, rule name, numerical fact, and research boundary. Add:

```html
<link rel="canonical" href="https://axioglyph.evemisslab.com/">
<meta property="og:url" content="https://axioglyph.evemisslab.com/">
```

- [ ] **Step 4: Verify site and browser behavior**

```powershell
python -B tests/test_site_content_v0.4.py -v
node tests/test_core_v0.4.js
python -B tools/empsl_v04_batch_check.py
.\.venv\Scripts\python.exe -B tests/test_browser_v0.4.py
```

Expected: 5 content tests, 30 core groups, 4,096 corpus cases, both downloads, and zero browser console errors.

- [ ] **Step 5: Commit the copy rewrite**

```powershell
git add -- empsl/v0.4/index.html empsl/v0.4/tests/test_site_content_v0.4.py
git commit -m "copy: make Axioglyph Chinese more conversational"
```

---

### Task 2: Build a bounded Worker asset package

**Files:**
- Create: `site/build.py`
- Create: `site/404.html`
- Create: `site/llms.txt`
- Create: `wrangler.jsonc`
- Create: `tests/test_axioglyph_bundle.py`
- Modify: `.gitignore`
- Modify: `empsl/v0.4/README.md`

**Interfaces:**
- Consumes: exact runtime source files under `empsl/v0.4`.
- Produces: `site/dist/` containing only the public runtime, discovery files, and 404 page; Wrangler reads that directory.

- [ ] **Step 1: Write the bundle test first**

The test runs `site/build.py`, then asserts this exact policy:

```python
required = {
    "index.html", "404.html", "robots.txt", "sitemap.xml", "llms.txt",
    "assets/site.css", "assets/site.js", "assets/app.js", "assets/empsl_core.js",
    "data/EMPSL_atom_registry_v0.2.js",
    "data/EMPSL_seed_variant_registry_v0.3.js",
    "data/EMPSL_legality_report_v0.4.js",
    "rules/EMPSL_grammar_tables_v0.4.js",
    "rules/EMPSL_rule_catalog_v0.4.js",
    "examples/EMPSL_legality_examples_v0.4.js",
}
self.assertEqual(required, public_files)
self.assertNotIn("tests", public_top_level)
self.assertNotIn("corpus", public_top_level)
self.assertNotIn("tools", public_top_level)
```

- [ ] **Step 2: Run it and confirm the missing-builder failure**

Run: `python -B tests/test_axioglyph_bundle.py -v`

Expected: FAIL because `site/build.py` does not exist.

- [ ] **Step 3: Implement the curated builder and public support files**

`site/build.py` resolves the repository root, removes only `site/dist`, copies the exact runtime list, copies the committed `site/404.html` and `site/llms.txt`, then writes:

```text
robots.txt: User-agent: *\nAllow: /\nSitemap: https://axioglyph.evemisslab.com/sitemap.xml
sitemap.xml: one URL, https://axioglyph.evemisslab.com/
```

The 404 page links back to `/`, includes `noindex`, and uses the same public brand. Add `site/dist/` to `.gitignore`.

- [ ] **Step 4: Configure the assets-only Worker**

Create `wrangler.jsonc`:

```jsonc
{
  "name": "axioglyph",
  "compatibility_date": "2026-08-22",
  "assets": {
    "directory": "./site/dist",
    "html_handling": "auto-trailing-slash",
    "not_found_handling": "404-page"
  },
  "routes": [
    { "pattern": "axioglyph.evemisslab.com", "custom_domain": true }
  ],
  "observability": { "enabled": true }
}
```

- [ ] **Step 5: Verify and commit the package boundary**

```powershell
python -B tests/test_axioglyph_bundle.py -v
npx.cmd wrangler deploy --dry-run
git diff --check
git add -- .gitignore site wrangler.jsonc tests/test_axioglyph_bundle.py empsl/v0.4/README.md
git commit -m "deploy: package Axioglyph as a static Worker"
```

---

### Task 3: Add Axioglyph to the EveMissLab parent index

**Files in `D:\Ai\網站群\evemisslab`:**
- Create: `tests/test_axioglyph_entry.py`
- Modify: `src/content.py`
- Modify: `src/assets/styles.css`
- Modify: `README.md`

**Interfaces:**
- Consumes: the live child URL and the parent renderer's paired EN/ZH groups.
- Produces: one English and one Traditional Chinese card under `systems`, using `tone="axioglyph"`; parent build count becomes 17.

- [ ] **Step 1: Write the paired-entry regression test**

```python
def find(lang):
    return [site for group in content.GROUPS[lang] for site in group["sites"] if site["host"] == "axioglyph"]

class AxioglyphIndexTests(unittest.TestCase):
    def test_both_languages_have_one_axioglyph_entry(self):
        self.assertEqual(1, len(find("en")))
        self.assertEqual(1, len(find("zh")))
        self.assertEqual("axioglyph", find("en")[0]["tone"])
        self.assertEqual("axioglyph", find("zh")[0]["tone"])

    def test_rendered_pages_link_to_the_live_child(self):
        subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True)
        for page in (ROOT / "dist/index.html", ROOT / "dist/zh/index.html"):
            html = page.read_text(encoding="utf-8")
            self.assertIn("https://axioglyph.evemisslab.com/", html)
            self.assertIn("17 sites", html)
```

- [ ] **Step 2: Run the test and observe the missing entry**

Run: `python -B tests/test_axioglyph_entry.py -v`

Expected: FAIL with zero matching entries.

- [ ] **Step 3: Add the bilingual card and colour token**

Add the approved English and Chinese descriptions to the `systems` group. Add `--t-axioglyph: #8e4d23` to light tokens and `--t-axioglyph: #e8aa6d` to both dark token blocks.

- [ ] **Step 4: Build, test, and commit**

```powershell
python -B tests/test_axioglyph_entry.py -v
python -B build.py
git diff --check
git add -- tests/test_axioglyph_entry.py src/content.py src/assets/styles.css README.md
git commit -m "feat: add Axioglyph to the EveMissLab index"
```

---

### Task 4: Push, deploy, and verify both public sites

**Files:**
- No new source files.
- Verify both repositories and both production domains.

**Interfaces:**
- Consumes: clean, committed `main` branches and configured Cloudflare credentials.
- Produces: synchronized GitHub branches, live child Worker, and updated parent Pages deployment.

- [ ] **Step 1: Run complete local verification in FARHP**

```powershell
python -B tests/test_axioglyph_bundle.py -v
python -B empsl/v0.4/tests/test_site_content_v0.4.py -v
node empsl/v0.4/tests/test_core_v0.4.js
python -B empsl/v0.4/tools/empsl_v04_batch_check.py
empsl\v0.4\.venv\Scripts\python.exe -B empsl/v0.4/tests/test_browser_v0.4.py
git status -sb
```

- [ ] **Step 2: Push FARHP and deploy the child Worker**

```powershell
git push origin main
python -B site/build.py
npx.cmd wrangler deploy
```

Poll the child with `?v=<HEAD-short-sha>` until HTTP 200 and the new conversational headline appear. Confirm a random missing path is HTTP 404.

- [ ] **Step 3: Run parent verification, push, and deploy Pages**

```powershell
python -B tests/test_axioglyph_entry.py -v
python -B build.py
git push origin main
npx.cmd wrangler pages deploy dist --project-name evemisslab
```

- [ ] **Step 4: Verify the live parent and cross-site relationship**

Poll `https://evemisslab.com/?v=<parent-sha>` and `/zh/?v=<parent-sha>` until both contain `axioglyph.evemisslab.com` and show `17 sites`. Open the card destination and confirm it returns the already-verified child page.

- [ ] **Step 5: Confirm clean synchronized repositories**

For both repositories run:

```powershell
git status -sb
git rev-parse HEAD
git rev-parse origin/main
```

Expected: clean `main`, local HEAD equals `origin/main`, child and parent production URLs both return the new content.
