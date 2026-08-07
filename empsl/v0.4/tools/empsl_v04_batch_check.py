#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,hashlib,collections
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v04',ROOT/'tools/empsl_v04_validate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
reg,vr,g,rc=m.maps();recipe_schema=m.load(ROOT/'spec/EMPSL_Glyph_Recipe_Spec_v0.4.schema.json');case_schema=m.load(ROOT/'spec/EMPSL_Validation_Case_Spec_v0.4.schema.json');rule_schema=m.load(ROOT/'spec/EMPSL_Rule_Catalog_Spec_v0.4.schema.json')
assert not list(Draft202012Validator(rule_schema).iter_errors(rc))
counts=collections.Counter();hits=collections.Counter();n=0
for line in (ROOT/'corpus/EMPSL_legality_corpus_v0.4.jsonl').read_text(encoding='utf-8').splitlines():
 case=json.loads(line);n+=1;assert not list(Draft202012Validator(case_schema).iter_errors(case));r=case['recipe'];cross=m.validate_cross(r,reg,vr,g,rc);stored=r['validation_certificate'];assert (cross['valid'],cross['error_count'],cross['warning_count'])==(stored['valid'],stored['error_count'],stored['warning_count']);assert [(x['rule_id'],x['severity'],x['field']) for x in cross['issues']]==[(x['rule_id'],x['severity'],x['field']) for x in stored['issues']];assert cross['valid']==case['expected_valid'];assert m.stable_hash(m.canonical_recipe(r))==r['recipe_sha256'];
 if cross['valid']:assert not list(Draft202012Validator(recipe_schema).iter_errors(r))
 counts[(case['generator'],cross['valid'])]+=1;hits.update(x['rule_id'] for x in cross['issues'])
report=m.load(ROOT/'data/EMPSL_legality_report_v0.4.json');assert n==report['sample_count']==4096;assert counts[('valid',True)]==1024;assert counts[('mutated-invalid',False)]==1024;assert counts[('fuzz',False)]==2048;assert dict(sorted(hits.items()))==report['rule_hit_counts']
print(f'PASS batch cross-validation · {n} cases · rules={rc["rule_count"]} · valid=1024 · invalid=3072')
