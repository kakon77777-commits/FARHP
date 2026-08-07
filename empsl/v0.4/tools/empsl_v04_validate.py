#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, re, sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def stable_hash(obj): return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def canonical_recipe(r):
 keys=['frame','seed_base','seed_transform','seed_variant','phonology','tone','phase','operator','transform_role','semantic','acoustic']
 return {k:r[k] for k in keys}

def maps():
 reg=load(ROOT/'data/EMPSL_atom_registry_v0.2.json'); vr=load(ROOT/'data/EMPSL_seed_variant_registry_v0.3.json'); g=load(ROOT/'rules/EMPSL_grammar_tables_v0.4.json'); rc=load(ROOT/'rules/EMPSL_rule_catalog_v0.4.json')
 return reg,vr,g,rc

def classify(recipe, atoms):
 out={'onset':[],'four_hu':[],'rime':[],'structure':[],'other':[]}
 for x in recipe.get('phonology',[]):
  st=atoms.get(x,{}).get('subtype')
  out[st if st in out else 'other'].append(x)
 return out

def infer_class(recipe, atoms, g):
 c=classify(recipe,atoms); onset=(c['onset'] or [None])[0]; rime=(c['rime'] or [None])[0]
 if 'ST-BOUNDARY' in c['structure']: return 'silent'
 noisy=set(g['noise'])|set(g['mixed'])
 if not rime:return 'noise_dominant' if onset in noisy else 'silent'
 return 'mixed' if onset in set(g['mixed']) else 'voiced_harmonic'

def validate_cross(r,reg,vr,g,rc):
 atoms={a['id']:a for a in reg['atoms']}; variants={v['id']:v for v in vr['variants']}; rules={x['id']:x for x in rc['rules']}; issues=[]
 def add(rule,severity,message,field='',suggestion=''):
  issues.append({'rule_id':rule,'severity':severity,'domain':rules[rule]['domain'],'message':message,'field':field,'suggestion':suggestion})
 if r.get('version')!='0.4':add('G-004','error','version 必須為 0.4','version','設為 0.4')
 ids=set(atoms)
 for k in ['frame','tone','phase','operator']:
  if r.get(k) not in ids:add('G-001','error',f'未知 {k}: {r.get(k)}',k,'選擇註冊表內 ID')
 for p in r.get('phonology',[]):
  if p not in ids:add('G-001','error',f'未知 phonology: {p}','phonology','移除或更換為已註冊附標')
 v=variants.get(r.get('seed_variant'))
 if not v:add('G-001','error',f"未知 seed_variant: {r.get('seed_variant')}",'seed_variant','選擇已註冊變體')
 elif v['base_seed']!=r.get('seed_base') or v['transform_id']!=r.get('seed_transform'):add('G-002','error','seed_base／seed_transform 與 seed_variant 不一致','seed_variant',f"改為 {r.get('seed_base')}@{r.get('seed_transform')}")
 if len(r.get('phonology',[]))>4:add('G-003','error','phonology 超過四個附標','phonology','每類只保留一個')
 c=classify(r,atoms)
 if len(set(r.get('phonology',[])))!=len(r.get('phonology',[])) or any(len(c[k])>1 for k in ['onset','four_hu','rime','structure']):add('P-001','error','音系附標重複或同類別超過一個','phonology','每類只保留一個')
 onset=(c['onset'] or [None])[0];hu=(c['four_hu'] or [None])[0];rime=(c['rime'] or [None])[0];st=(c['structure'] or [None])[0]
 if onset and hu and hu not in set(g['onset_hus'].get(onset,[])):add('P-002','error',f'{onset} 不接受 {hu}','phonology','更換四呼或聲母')
 if hu and rime and rime not in set(g['hu_rimes'].get(hu,[])):add('P-003','error',f'{hu} 不接受 {rime}','phonology','更換韻類')
 if rime=='RIME-ER' and (onset or (hu and hu!='HU-KAIKOU') or st=='ST-RHOTIC'):add('P-004','error','RIME-ER 只允許零聲母開口呼，且不可再加 ST-RHOTIC','phonology','移除聲母／兒化附標並改用開口呼')
 if r.get('tone')=='T0' and st!='ST-LIGHT':add('P-005','warning','T0 建議加入 ST-LIGHT','tone','加入 ST-LIGHT')
 if st=='ST-LIGHT' and r.get('tone')!='T0':add('P-005','error','ST-LIGHT 必須使用 T0','tone','將聲調改為 T0')
 if st=='ST-NASAL' and rime not in set(g['nasal']):add('P-006','error','ST-NASAL 需要 AN／EN／ANG／ENG','phonology','更換鼻韻或移除 ST-NASAL')
 if st=='ST-ZERO' and onset:add('P-007','error','ST-ZERO 不可與聲母共現','phonology','移除聲母')
 if st=='ST-BOUNDARY' and (onset or hu or rime or r.get('tone')!='T0' or r.get('phase')!='PH16-00'):add('P-008','error','ST-BOUNDARY 必須排他並使用 T0／PH16-00','phonology','清除聲母四呼韻類，設 T0 與 PH16-00')
 if st=='ST-RHOTIC' and rime=='RIME-ER':add('P-009','error','兒化不得與 RIME-ER 重複編碼','phonology','保留其中一種兒化表示')
 if st!='ST-BOUNDARY' and not rime:add('P-010','error','非邊界詞素缺少韻類','phonology','加入 RIME-*')
 if hu and not rime:add('P-010','error','四呼不可沒有韻類','phonology','加入相容韻類')
 sem=r.get('semantic') or {};kind=sem.get('kind');op=r.get('operator');tr=r.get('seed_transform');role=r.get('transform_role')
 if role not in set(g['trans_roles'].get(tr,[])):add('T-001','error',f'{tr} 不接受 transform_role={role}','transform_role','更換角色')
 if kind not in set(g['trans_kinds'].get(tr,[])):add('T-002','error',f'{tr} 不適用於 semantic.kind={kind}','semantic.kind','更換變換或語義種類')
 if (kind=='delimiter' or st=='ST-BOUNDARY') and tr!='ID':add('T-003','error','邊界／delimiter 只能使用 ID 變換','seed_transform','設為 ID')
 idpat=re.compile(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*:[a-z][a-z0-9_-]*:[0-9a-z_-]+$')
 if not idpat.match(sem.get('concept_id','')):add('S-001','error','concept_id 不符合三段式穩定 ID','semantic.concept_id','使用 eml.concept:item:local-id 格式')
 if kind not in set(g['op_kind'].get(op,[])):add('S-002','error',f'{op} 不接受 semantic.kind={kind}','semantic.kind','更換 semantic.kind 或 operator')
 sig=sem.get('signature') or {};ar=sig.get('arity') or {};inputs=sig.get('inputs') or [];expected=g['op_arity'].get(op)
 if expected:
  mode,n=expected
  if ar.get('mode')!=mode:add('S-003','error',f'{op} 需要 arity.mode={mode}','semantic.signature.arity','修正參數模式')
  if mode=='fixed':
   if ar.get('value')!=n:add('S-003','error',f'{op} 需要 fixed arity={n}','semantic.signature.arity.value',f'設為 {n}')
   if len(inputs)!=n:add('S-004','error',f'inputs 長度 {len(inputs)} 與 arity {n} 不符','semantic.signature.inputs',f'提供 {n} 個輸入型別')
  elif ar.get('min',-1)<n:add('S-003','error',f'{op} 需要 variadic min>={n}','semantic.signature.arity.min',f'設為 {n}')
 if r.get('frame') not in set(g['op_frames'].get(op,[])):add('S-005','error',f'{op} 不適用於 {r.get("frame")}','frame','選擇相容外框')
 out=sig.get('output');exp=g['frame_out'].get(r.get('frame'))
 if out and exp and out!=exp:add('S-006','warning',f'輸出型別 {out} 與外框建議 {exp} 不同','semantic.signature.output',f'改為 {exp} 或記錄偏離理由')
 ac=r.get('acoustic') or {};inf=infer_class(r,atoms,g)
 if ac.get('phase_signature')!=r.get('phase'):add('A-001','error','acoustic.phase_signature 與字形 phase 不一致','acoustic.phase_signature',f"改為 {r.get('phase')}")
 if ac.get('class')!=inf:add('A-002','error',f"acoustic.class={ac.get('class')}，推導值為 {inf}",'acoustic.class',f'改為 {inf}')
 if inf=='silent':
  if ac.get('source')!='NONE' or r.get('phase')!='PH16-00' or ac.get('profile_id') is not None:add('A-003','error','silent 必須 source=NONE、PH16-00、profile_id=null','acoustic','清除 FARHP 資料')
 elif ac.get('source')=='NONE' or not ac.get('profile_id'):add('A-004','error','非 silent 必須指定 FARHP 來源與 profile_id','acoustic','設定 FARHP-Y 與 profile_id')
 if inf=='noise_dominant' and r.get('phase')!='PH16-00':add('A-005','warning','噪聲主導音的非零 PH16 僅作弱控制量','phase','保留但降低可靠度，或設 PH16-00')
 if ac.get('source')=='FARHP-G' and inf in {'noise_dominant','silent'}:add('A-006','warning','此聲學類別不適合直接解釋為 FARHP-G','acoustic.source','改用 FARHP-Y 或 NONE')
 if inf!='silent' and float(ac.get('confidence',0))<0.5:add('A-007','warning','FARHP confidence 低於 0.5，不宜作硬判定','acoustic.confidence','提高資料品質或保留為低信心度標記')
 errors=[x for x in issues if x['severity']=='error'];warnings=[x for x in issues if x['severity']=='warning']
 return {'valid':not errors,'status':'PASS' if not errors else 'FAIL','error_count':len(errors),'warning_count':len(warnings),'issues':issues,'ruleset_sha256':rc['ruleset_sha256']}

def validate_file(path,quiet=False):
 reg,vr,g,rc=maps();schema=load(ROOT/'spec/EMPSL_Glyph_Recipe_Spec_v0.4.schema.json');data=load(path);is_bundle=isinstance(data,dict) and 'recipes' in data;recipes=data.get('recipes') if is_bundle else [data];ok=True
 for i,r in enumerate(recipes):
  errs=list(Draft202012Validator(schema).iter_errors(r));cross=validate_cross(r,reg,vr,g,rc);stored=r.get('validation_certificate');h=stable_hash(canonical_recipe(r));schema_ok=(not errs) if cross['valid'] else True;local_ok=schema_ok and stored==cross and h==r.get('recipe_sha256')
  if not is_bundle: local_ok=local_ok and cross['valid'] and not errs
  if not quiet:print(('PASS' if local_ok else 'FAIL'),Path(path).name,f'#{i}',f"schema={len(errs)} cross={cross['status']} hash={h==r.get('recipe_sha256')}")
  if not local_ok:
   ok=False
   if errs and not quiet:print(' schema:',errs[0].message)
   if stored!=cross and not quiet:print(' certificate mismatch')
 return ok

def main():
 ap=argparse.ArgumentParser(description='Validate EMPSL v0.4 recipe JSON and legality certificate.');ap.add_argument('files',nargs='*');ap.add_argument('--quiet',action='store_true');args=ap.parse_args();files=args.files or [str(ROOT/'examples/EMPSL_legality_examples_v0.4.json')];ok=all(validate_file(f,args.quiet) for f in files);return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
