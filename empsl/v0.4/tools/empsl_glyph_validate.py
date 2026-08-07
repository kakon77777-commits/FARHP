#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
REG=json.loads((ROOT/'data/EMPSL_atom_registry_v0.2.json').read_text(encoding='utf-8'))
MAP={a['id']:a for a in REG['atoms']}
SCHEMA=json.loads((ROOT/'spec/EMPSL_Glyph_Recipe_Spec_v0.2.schema.json').read_text(encoding='utf-8'))

def canonical(recipe):
    core={k:recipe[k] for k in ['frame','seed','phonology','tone','phase','operator']}
    return json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('json_file');args=ap.parse_args()
    obj=json.loads(Path(args.json_file).read_text(encoding='utf-8'))
    recipes=obj.get('recipes',[obj])
    errors=[]
    for i,r in enumerate(recipes):
        try: jsonschema.validate(r,SCHEMA)
        except Exception as e: errors.append(f'{i}: schema: {e.message}')
        expected=hashlib.sha256(canonical(r).encode()).hexdigest()
        if r.get('recipe_sha256')!=expected: errors.append(f'{i}: recipe_sha256 mismatch')
        for atom in [r.get('frame'),r.get('seed'),r.get('tone'),r.get('phase'),r.get('operator'),*(r.get('phonology') or [])]:
            if atom not in MAP: errors.append(f'{i}: unknown atom {atom}')
    if errors:
        print('FAIL');print('\n'.join(errors));return 1
    print(f'PASS recipes={len(recipes)} atoms={REG["count"]}')
    return 0
if __name__=='__main__': raise SystemExit(main())
