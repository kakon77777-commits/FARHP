#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, sys, xml.etree.ElementTree as ET
from collections import Counter
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def check(name,cond,details=''):
 print(('PASS' if cond else 'FAIL')+' · '+name+((' · '+details) if details else ''));return bool(cond)
def main():
 ok=[];reg=load('data/EMPSL_atom_registry_v0.2.json');vr=load('data/EMPSL_seed_variant_registry_v0.3.json');col=load('data/EMPSL_collision_report_v0.3.json');samples=load('data/EMPSL_sample_recipes_v0.3.json')
 vschema=load('spec/EMPSL_Seed_Variant_Registry_Spec_v0.3.schema.json');rschema=load('spec/EMPSL_Glyph_Recipe_Spec_v0.3.schema.json')
 ok.append(check('base atoms = 128',reg['count']==128));ok.append(check('variants = 256',vr['count']==256));ok.append(check('transforms = 8',vr['transform_count']==8));ok.append(check('variant ids unique',len({v['id'] for v in vr['variants']})==256));ok.append(check('variant indices unique',len({v['variant_index'] for v in vr['variants']})==256));
 c=Counter(v['base_seed'] for v in vr['variants']);ok.append(check('8 variants per seed',set(c.values())=={8}));c=Counter(v['transform_id'] for v in vr['variants']);ok.append(check('32 seeds per transform',set(c.values())=={32}));
 errs=list(Draft202012Validator(vschema).iter_errors(vr));ok.append(check('variant registry schema',not errs,errs[0].message if errs else ''))
 svg_ok=True;hash_ok=True
 for v in vr['variants']:
  p=ROOT/'assets/variants'/(v['id'].replace('@','--')+'.svg');q=ROOT/'assets/variants_raw'/(v['id'].replace('@','--')+'.svg')
  try:ET.parse(p);ET.parse(q)
  except Exception:svg_ok=False
  if hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest()!=v['svg_sha256']:hash_ok=False
  if hashlib.sha256(q.read_text(encoding='utf-8').encode()).hexdigest()!=v['raw_svg_sha256']:hash_ok=False
 ok.append(check('512 SVG files parse',svg_ok));ok.append(check('variant SVG hashes round-trip',hash_ok));ok.append(check('canonical exact collisions = 0',col['variant_layer']['canonical_exact_collision_group_count']==0));ok.append(check('composite sample count = 8192',col['composite_layer']['sample_count']==8192));ok.append(check('composite unique recipes = 8192',col['composite_layer']['unique_recipe_count']==8192));
 lines=(ROOT/'data/EMPSL_composite_collision_corpus_v0.3.jsonl').read_text(encoding='utf-8').splitlines();ok.append(check('corpus lines = 8192',len(lines)==8192));
 sample_ok=True;sample_hash=True
 for r in samples['recipes']:
  if list(Draft202012Validator(rschema).iter_errors(r)):sample_ok=False
  core={k:r[k] for k in ['frame','seed_base','seed_transform','seed_variant','phonology','tone','phase','operator']};h=hashlib.sha256(json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  if h!=r['recipe_sha256']:sample_hash=False
 ok.append(check('sample recipe schema',sample_ok));ok.append(check('sample recipe hashes',sample_hash));
 for f in ['assets/charts/EMPSL_256_seed_variant_chart_v0.3.png','assets/charts/EMPSL_collision_diagnostics_v0.3.png','index.html','assets/app.js','assets/empsl_core.js']:
  ok.append(check('exists '+f,(ROOT/f).exists()))
 print(f'RESULT · {sum(ok)}/{len(ok)} PASS');return 0 if all(ok) else 1
if __name__=='__main__':raise SystemExit(main())
