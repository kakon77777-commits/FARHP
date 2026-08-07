from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8')
for rel in ['data/EMPSL_atom_registry_v0.2.js','data/EMPSL_seed_variant_registry_v0.3.js','rules/EMPSL_grammar_tables_v0.4.js','rules/EMPSL_rule_catalog_v0.4.js','data/EMPSL_legality_report_v0.4.js','examples/EMPSL_legality_examples_v0.4.js','assets/empsl_core.js','assets/app.js']:
 html=html.replace(f'<script src="{rel}"></script>',f'<script>\n{(ROOT/rel).read_text(encoding="utf-8")}\n</script>')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
 errors=[];page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None);page.on('pageerror',lambda e: errors.append(str(e)))
 page.set_content(html,wait_until='load',timeout=30000)
 page.wait_for_function('window.EMPSL_V04_READY===true')
 assert page.locator('#status').inner_text().startswith('PASS')
 assert page.locator('#ruleGrid .rule').count()==30
 assert page.locator('#variantGallery .atom-card').count()==8
 page.screenshot(path=str(ROOT/'assets/preview_v0.4.png'),full_page=True)
 page.click('#invalidExample');page.wait_for_timeout(250)
 assert page.locator('#status').inner_text().startswith('FAIL')
 assert page.locator('#issues .issue').count()>0
 page.click('#repair');page.wait_for_timeout(300)
 assert page.locator('#status').inner_text().startswith('PASS')
 page.select_option('#onset','ONSET-G');page.select_option('#hu','HU-CUOKOU');page.select_option('#rime','RIME-AI');page.wait_for_timeout(250)
 txt=page.locator('#issues').inner_text();assert 'P-002' in txt and 'P-003' in txt
 page.click('#repair');page.wait_for_timeout(300);assert page.locator('#status').inner_text().startswith('PASS')
 assert not errors,errors
 print('PASS browser v0.4 · rules=30 · variants=8 · console_errors=0')
 browser.close()
