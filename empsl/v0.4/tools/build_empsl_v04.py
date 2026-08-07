from pathlib import Path
import json, hashlib, random, re, copy, collections, math
ROOT=Path('/mnt/data/EMPSL_v0.4')
REG=json.loads((ROOT/'data/EMPSL_atom_registry_v0.2.json').read_text(encoding='utf-8'))
VAR=json.loads((ROOT/'data/EMPSL_seed_variant_registry_v0.3.json').read_text(encoding='utf-8'))
AT={a['id']:a for a in REG['atoms']}

RULES=[
 {'id':'G-001','domain':'glyph','severity':'error','title':'原子與變體必須存在','description':'所有槽位 ID 必須存在於原子或種子變體註冊表。'},
 {'id':'G-002','domain':'glyph','severity':'error','title':'種子三欄必須一致','description':'seed_base、seed_transform 與 seed_variant 必須描述同一變體。'},
 {'id':'G-003','domain':'glyph','severity':'error','title':'音系槽不得超過四個','description':'六槽模型的音系區最多容納四個附標。'},
 {'id':'G-004','domain':'glyph','severity':'error','title':'配方版本必須為 0.4','description':'v0.4 合法性證書只適用於 0.4 配方。'},
 {'id':'P-001','domain':'phonology','severity':'error','title':'音系類別不得重複','description':'聲母、四呼、韻類與結構附標各最多一個，且不得重複 ID。'},
 {'id':'P-002','domain':'phonology','severity':'error','title':'聲母與四呼必須相容','description':'舌面音、舌尖音與舌根音具有不同四呼限制。'},
 {'id':'P-003','domain':'phonology','severity':'error','title':'四呼與韻類必須相容','description':'撮口呼、齊齒呼、合口呼與開口呼只接受規格表中的韻類。'},
 {'id':'P-004','domain':'phonology','severity':'error','title':'ㄦ韻使用限制','description':'RIME-ER 只允許零聲母、開口呼，且不能再加兒化附標。'},
 {'id':'P-005','domain':'phonology','severity':'warning','title':'輕聲與弱化附標一致','description':'T0 建議搭配 ST-LIGHT；ST-LIGHT 若非 T0 則為錯誤。'},
 {'id':'P-006','domain':'phonology','severity':'error','title':'鼻尾附標必須有鼻韻','description':'ST-NASAL 只可搭配 AN、EN、ANG、ENG。'},
 {'id':'P-007','domain':'phonology','severity':'error','title':'零聲母附標必須無聲母','description':'ST-ZERO 與任何 ONSET-* 不可共現。'},
 {'id':'P-008','domain':'phonology','severity':'error','title':'邊界符號必須排他','description':'ST-BOUNDARY 不得攜帶聲母、四呼或韻類，並使用 T0、PH16-00。'},
 {'id':'P-009','domain':'phonology','severity':'error','title':'兒化不得重複編碼','description':'ST-RHOTIC 不得與 RIME-ER 或 ST-NASAL 同時使用。'},
 {'id':'P-010','domain':'phonology','severity':'error','title':'可發音詞素必須有韻類','description':'非邊界詞素至少要有一個 RIME-*；四呼也不可孤立。'},
 {'id':'T-001','domain':'transform','severity':'error','title':'變換角色必須相容','description':'不同幾何變換只允許指定的 identity、allographic、semantic_modifier 或 structural 角色。'},
 {'id':'T-002','domain':'transform','severity':'error','title':'變換與語義種類必須相容','description':'開口、內嵌與交叉等變換不可任意套用到所有語義種類。'},
 {'id':'T-003','domain':'transform','severity':'error','title':'邊界符號不得作語義變換','description':'delimiter／ST-BOUNDARY 只使用原形 ID。'},
 {'id':'S-001','domain':'semantics','severity':'error','title':'概念 ID 必須穩定','description':'concept_id 採 namespace:kind:local-id 三段式。'},
 {'id':'S-002','domain':'semantics','severity':'error','title':'語義種類與算子必須相容','description':'item、operator、binder、delimiter、meta 等種類各有允許算子。'},
 {'id':'S-003','domain':'semantics','severity':'error','title':'算子參數模式必須相符','description':'固定參數與可變參數模式必須符合算子定義。'},
 {'id':'S-004','domain':'semantics','severity':'error','title':'固定參數數量必須相符','description':'fixed arity 的 inputs 長度必須等於 value。'},
 {'id':'S-005','domain':'semantics','severity':'error','title':'語義外框與算子必須相容','description':'因果、否定、時態、模態等算子只能放入對應外框。'},
 {'id':'S-006','domain':'semantics','severity':'warning','title':'輸出型別應符合外框','description':'semantic.signature.output 建議與語義外框的標準輸出型別一致。'},
 {'id':'A-001','domain':'acoustics','severity':'error','title':'可視相位與聲學簽名一致','description':'acoustic.phase_signature 必須等於字形 PH16 槽位。'},
 {'id':'A-002','domain':'acoustics','severity':'error','title':'聲學類別必須可推導','description':'voiced_harmonic、mixed、noise_dominant、silent 應由音節結構推導。'},
 {'id':'A-003','domain':'acoustics','severity':'error','title':'靜音物件不得攜帶 FARHP','description':'silent 必須 source=NONE、phase=PH16-00、profile_id=null。'},
 {'id':'A-004','domain':'acoustics','severity':'error','title':'有聲物件必須指定 FARHP 來源','description':'非 silent 物件不可使用 NONE，且必須有 profile_id。'},
 {'id':'A-005','domain':'acoustics','severity':'warning','title':'噪聲主導音的相位只是弱控制量','description':'noise_dominant 使用非零 PH16 時只視為近似標記。'},
 {'id':'A-006','domain':'acoustics','severity':'warning','title':'FARHP-G 需要可逆濾波語境','description':'FARHP-G 用於聲門估計；噪聲主導或無韻核時可靠度較低。'},
 {'id':'A-007','domain':'acoustics','severity':'warning','title':'低信心度相位不得作硬判定','description':'非靜音物件若 confidence < 0.5，只可作近似聲學標記。'},
]
RULESET={'spec_version':'0.4','title':'EMPSL Glyph Grammar Rule Catalog','rule_count':len(RULES),'rules':RULES}
canon=json.dumps(RULESET,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
RULESET['ruleset_sha256']=hashlib.sha256(canon).hexdigest()
(ROOT/'rules/EMPSL_rule_catalog_v0.4.json').write_text(json.dumps(RULESET,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'rules/EMPSL_rule_catalog_v0.4.js').write_text('window.EMPSL_RULE_CATALOG='+json.dumps(RULESET,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')

# Shared data
FRAMES=[a['id'] for a in REG['atoms'] if a['category']=='semantic_frame']
SEEDS=[a['id'] for a in REG['atoms'] if a['category']=='seed']
TRANS=[t['id'] for t in VAR['transforms']]
PHASES=[a['id'] for a in REG['atoms'] if a['category']=='phase_mark']
OPS=[a['id'] for a in REG['atoms'] if a['category']=='operator_mark']
ONSETS=[a['id'] for a in REG['atoms'] if a.get('subtype')=='onset']
HUS=[a['id'] for a in REG['atoms'] if a.get('subtype')=='four_hu']
RIMES=[a['id'] for a in REG['atoms'] if a.get('subtype')=='rime']
TONES=[a['id'] for a in REG['atoms'] if a.get('subtype')=='tone']
STRUCTS=[a['id'] for a in REG['atoms'] if a.get('subtype')=='structure']
TYPES=['Any','Entity','Event','Relation','Property','Quantity','Time','Space','Modality','Evidence','Agent','Information','Permission','Boolean','Collection','Meta']
KINDS=['item','predicate','operator','binder','delimiter','meta']
ROLES=['identity','allographic','semantic_modifier','structural']
SOURCES=['NONE','FARHP-Y','FARHP-G']
CLASSES=['voiced_harmonic','mixed','noise_dominant','silent']

OP_ARITY={
 'OP-NULL':('fixed',0),'OP-UNARY':('fixed',1),'OP-BINARY':('fixed',2),'OP-TERNARY':('fixed',3),'OP-VARIADIC':('variadic',1),
 'OP-BIND':('fixed',2),'OP-QUOTE':('fixed',1),'OP-META':('fixed',1),'OP-TEMP':('fixed',1),'OP-MODAL':('fixed',1),'OP-NEG':('fixed',1),
 'OP-CAUSE':('fixed',2),'OP-AGG':('variadic',1),'OP-MAP':('fixed',2),'OP-REDUCE':('fixed',2),'OP-GUARD':('fixed',2)}
OP_KIND={
 'OP-NULL':{'item','delimiter'},'OP-BIND':{'binder'},'OP-QUOTE':{'meta'},'OP-META':{'meta'},
 'OP-UNARY':{'predicate','operator'},'OP-BINARY':{'predicate','operator'},'OP-TERNARY':{'predicate','operator'},'OP-VARIADIC':{'predicate','operator'},
 'OP-TEMP':{'predicate','operator'},'OP-MODAL':{'predicate','operator'},'OP-NEG':{'predicate','operator'},'OP-CAUSE':{'predicate','operator'},
 'OP-AGG':{'predicate','operator'},'OP-MAP':{'predicate','operator'},'OP-REDUCE':{'predicate','operator'},'OP-GUARD':{'predicate','operator'}}
OP_FRAMES={
 'OP-NULL':set(FRAMES),'OP-UNARY':{'SEM-PROPERTY','SEM-RELATION','SEM-PROCESS','SEM-META'},'OP-BINARY':{'SEM-RELATION','SEM-PROCESS','SEM-META'},
 'OP-TERNARY':{'SEM-RELATION','SEM-PROCESS','SEM-META'},'OP-VARIADIC':{'SEM-RELATION','SEM-AGGREGATION','SEM-META'},'OP-BIND':{'SEM-META','SEM-RELATION'},
 'OP-QUOTE':{'SEM-INFORMATION','SEM-META'},'OP-META':{'SEM-META','SEM-INFORMATION'},'OP-TEMP':{'SEM-TIME','SEM-PROCESS'},'OP-MODAL':{'SEM-MODALITY','SEM-PERMISSION'},
 'OP-NEG':{'SEM-NEGATION','SEM-MODALITY'},'OP-CAUSE':{'SEM-CAUSALITY','SEM-RELATION','SEM-PROCESS'},'OP-AGG':{'SEM-AGGREGATION','SEM-QUANTITY'},
 'OP-MAP':{'SEM-PROCESS','SEM-META'},'OP-REDUCE':{'SEM-PROCESS','SEM-AGGREGATION','SEM-META'},'OP-GUARD':{'SEM-PERMISSION','SEM-MODALITY','SEM-RELATION'}}
FRAME_OUT={'SEM-ENTITY':'Entity','SEM-PROCESS':'Event','SEM-RELATION':'Relation','SEM-PROPERTY':'Property','SEM-QUANTITY':'Quantity','SEM-TIME':'Time','SEM-SPACE':'Space','SEM-MODALITY':'Modality','SEM-CAUSALITY':'Relation','SEM-EVIDENCE':'Evidence','SEM-AGENT':'Agent','SEM-INFORMATION':'Information','SEM-PERMISSION':'Permission','SEM-NEGATION':'Boolean','SEM-AGGREGATION':'Collection','SEM-META':'Meta'}
TRANS_ROLES={'ID':{'identity','allographic'},'R90':{'allographic','semantic_modifier'},'R180':{'allographic','semantic_modifier'},'MX':{'allographic','semantic_modifier'},'OPEN-R':{'semantic_modifier'},'CLOSED':{'semantic_modifier','structural'},'INSET':{'semantic_modifier','structural'},'CROSS':{'semantic_modifier'}}
TRANS_KINDS={'ID':set(KINDS),'R90':set(KINDS)-{'delimiter'},'R180':set(KINDS)-{'delimiter'},'MX':set(KINDS)-{'delimiter'},'OPEN-R':{'predicate','operator','meta'},'CLOSED':{'item','predicate','operator','meta'},'INSET':{'operator','binder','meta'},'CROSS':{'predicate','operator'}}
HU_RIMES={
 'HU-KAIKOU':set(RIMES),
 'HU-QICHI':{'RIME-A','RIME-O','RIME-E','RIME-AO','RIME-OU','RIME-AN','RIME-EN','RIME-ANG','RIME-ENG'},
 'HU-HEKOU':{'RIME-A','RIME-O','RIME-E','RIME-AI','RIME-EI','RIME-AN','RIME-EN','RIME-ANG','RIME-ENG'},
 'HU-CUOKOU':{'RIME-E','RIME-AN','RIME-EN'} }
ONSET_HUS={}
for o in ONSETS: ONSET_HUS[o]={'HU-KAIKOU','HU-QICHI','HU-HEKOU','HU-CUOKOU'}
for o in ['ONSET-J','ONSET-Q','ONSET-X']: ONSET_HUS[o]={'HU-QICHI','HU-CUOKOU'}
for o in ['ONSET-ZH','ONSET-CH','ONSET-SH','ONSET-R','ONSET-Z','ONSET-C','ONSET-S']: ONSET_HUS[o]={'HU-KAIKOU','HU-HEKOU'}
for o in ['ONSET-G','ONSET-K','ONSET-H']: ONSET_HUS[o]={'HU-KAIKOU','HU-HEKOU'}
for o in ['ONSET-B','ONSET-P','ONSET-M','ONSET-F']: ONSET_HUS[o]={'HU-KAIKOU','HU-QICHI'}
for o in ['ONSET-D','ONSET-T']: ONSET_HUS[o]={'HU-KAIKOU','HU-QICHI','HU-HEKOU'}
for o in ['ONSET-N','ONSET-L']: ONSET_HUS[o]={'HU-KAIKOU','HU-QICHI','HU-HEKOU','HU-CUOKOU'}
NOISE={'ONSET-F','ONSET-H','ONSET-X','ONSET-SH','ONSET-S'}
MIXED={'ONSET-P','ONSET-T','ONSET-K','ONSET-Q','ONSET-CH','ONSET-C','ONSET-J','ONSET-ZH','ONSET-Z'}|NOISE
NASAL={'RIME-AN','RIME-EN','RIME-ANG','RIME-ENG'}
IDPAT=re.compile(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*:[a-z][a-z0-9_-]*:[0-9a-z_-]+$')

def cats(recipe):
 out={'onset':[],'four_hu':[],'rime':[],'structure':[],'other':[]}
 for x in recipe.get('phonology',[]):
  a=AT.get(x); st=a.get('subtype') if a else None
  (out[st] if st in out else out['other']).append(x)
 return out

def inferred_acoustic(recipe):
 c=cats(recipe); onset=c['onset'][0] if c['onset'] else None; rime=c['rime'][0] if c['rime'] else None; st=c['structure']
 if 'ST-BOUNDARY' in st: return 'silent'
 if not rime: return 'noise_dominant' if onset in NOISE|MIXED else 'silent'
 if onset in MIXED: return 'mixed'
 return 'voiced_harmonic'

def issue(rule,sev,msg,field='',suggestion=''):
 return {'rule_id':rule,'severity':sev,'domain':next(r['domain'] for r in RULES if r['id']==rule),'message':msg,'field':field,'suggestion':suggestion}

def validate(r):
 iss=[]; ids=set(AT); variants={v['id']:v for v in VAR['variants']};
 if r.get('version')!='0.4': iss.append(issue('G-004','error','version 必須為 0.4','version','設為 0.4'))
 for k in ['frame','tone','phase','operator']:
  if r.get(k) not in ids: iss.append(issue('G-001','error',f'未知 {k}: {r.get(k)}',k,'選擇註冊表內 ID'))
 for x in r.get('phonology',[]):
  if x not in ids: iss.append(issue('G-001','error',f'未知 phonology: {x}','phonology','移除或換成已註冊附標'))
 v=variants.get(r.get('seed_variant'))
 if not v: iss.append(issue('G-001','error',f"未知 seed_variant: {r.get('seed_variant')}",'seed_variant','選擇已註冊變體'))
 else:
  if v['base_seed']!=r.get('seed_base') or v['transform_id']!=r.get('seed_transform'):
   iss.append(issue('G-002','error','seed_base／seed_transform 與 seed_variant 不一致','seed_variant',f"改為 {r.get('seed_base')}@{r.get('seed_transform')}"))
 if len(r.get('phonology',[]))>4: iss.append(issue('G-003','error','phonology 超過四個附標','phonology','保留聲母、四呼、韻類與一個結構附標'))
 c=cats(r)
 if len(set(r.get('phonology',[])))!=len(r.get('phonology',[])) or any(len(c[k])>1 for k in ['onset','four_hu','rime','structure']):
  iss.append(issue('P-001','error','音系附標重複或同類別超過一個','phonology','每類只保留一個'))
 onset=c['onset'][0] if c['onset'] else None; hu=c['four_hu'][0] if c['four_hu'] else None; rime=c['rime'][0] if c['rime'] else None; st=c['structure'][0] if c['structure'] else None
 if onset and hu and hu not in ONSET_HUS.get(onset,set()): iss.append(issue('P-002','error',f'{onset} 不接受 {hu}','phonology','更換四呼或聲母'))
 if hu and rime and rime not in HU_RIMES.get(hu,set()): iss.append(issue('P-003','error',f'{hu} 不接受 {rime}','phonology','更換韻類'))
 if rime=='RIME-ER' and (onset or (hu and hu!='HU-KAIKOU') or st=='ST-RHOTIC'):
  iss.append(issue('P-004','error','RIME-ER 只允許零聲母開口呼，且不可再加 ST-RHOTIC','phonology','移除聲母／兒化附標並改用開口呼'))
 if r.get('tone')=='T0' and st!='ST-LIGHT': iss.append(issue('P-005','warning','T0 建議加入 ST-LIGHT','tone','加入 ST-LIGHT'))
 if st=='ST-LIGHT' and r.get('tone')!='T0': iss.append(issue('P-005','error','ST-LIGHT 必須使用 T0','tone','將聲調改為 T0'))
 if st=='ST-NASAL' and rime not in NASAL: iss.append(issue('P-006','error','ST-NASAL 需要 AN／EN／ANG／ENG','phonology','更換鼻韻或移除 ST-NASAL'))
 if st=='ST-ZERO' and onset: iss.append(issue('P-007','error','ST-ZERO 不可與聲母共現','phonology','移除聲母'))
 if st=='ST-BOUNDARY':
  if onset or hu or rime or r.get('tone')!='T0' or r.get('phase')!='PH16-00': iss.append(issue('P-008','error','ST-BOUNDARY 必須排他並使用 T0／PH16-00','phonology','清除聲母四呼韻類，設 T0 與 PH16-00'))
 if st=='ST-RHOTIC' and (rime=='RIME-ER' or rime in NASAL and False): iss.append(issue('P-009','error','兒化不得與 RIME-ER 重複編碼','phonology','保留其中一種兒化表示'))
 if st!='ST-BOUNDARY' and not rime: iss.append(issue('P-010','error','非邊界詞素缺少韻類','phonology','加入 RIME-*'))
 if hu and not rime: iss.append(issue('P-010','error','四呼不可沒有韻類','phonology','加入相容韻類'))
 sem=r.get('semantic') or {}; kind=sem.get('kind'); op=r.get('operator'); role=r.get('transform_role'); tr=r.get('seed_transform')
 if role not in TRANS_ROLES.get(tr,set()): iss.append(issue('T-001','error',f'{tr} 不接受 transform_role={role}','transform_role',f"改為 {sorted(TRANS_ROLES.get(tr,set()))[0] if TRANS_ROLES.get(tr) else 'identity'}"))
 if kind not in TRANS_KINDS.get(tr,set()): iss.append(issue('T-002','error',f'{tr} 不適用於 semantic.kind={kind}','semantic.kind','更換變換或語義種類'))
 if (kind=='delimiter' or st=='ST-BOUNDARY') and tr!='ID': iss.append(issue('T-003','error','邊界／delimiter 只能使用 ID 變換','seed_transform','設為 ID'))
 cid=sem.get('concept_id','')
 if not IDPAT.match(cid): iss.append(issue('S-001','error','concept_id 不符合三段式穩定 ID','semantic.concept_id','使用 eml.concept:item:local-id 格式'))
 if kind not in OP_KIND.get(op,set()): iss.append(issue('S-002','error',f'{op} 不接受 semantic.kind={kind}','semantic.kind','更換 semantic.kind 或 operator'))
 ar=sem.get('signature',{}).get('arity',{}); inputs=sem.get('signature',{}).get('inputs',[]); expected=OP_ARITY.get(op)
 if expected:
  mode,n=expected
  if ar.get('mode')!=mode: iss.append(issue('S-003','error',f'{op} 需要 arity.mode={mode}','semantic.signature.arity','修正參數模式'))
  if mode=='fixed':
   if ar.get('value')!=n: iss.append(issue('S-003','error',f'{op} 需要 fixed arity={n}','semantic.signature.arity.value',f'設為 {n}'))
   if len(inputs)!=n: iss.append(issue('S-004','error',f'inputs 長度 {len(inputs)} 與 arity {n} 不符','semantic.signature.inputs',f'提供 {n} 個輸入型別'))
  else:
   if ar.get('min',0)<n: iss.append(issue('S-003','error',f'{op} 需要 variadic min>={n}','semantic.signature.arity.min',f'設為 {n}'))
 if r.get('frame') not in OP_FRAMES.get(op,set()): iss.append(issue('S-005','error',f'{op} 不適用於 {r.get("frame")}','frame','選擇相容外框'))
 out=sem.get('signature',{}).get('output')
 expout=FRAME_OUT.get(r.get('frame'))
 if out and expout and out!=expout: iss.append(issue('S-006','warning',f'輸出型別 {out} 與外框建議 {expout} 不同','semantic.signature.output',f'改為 {expout} 或記錄偏離理由'))
 ac=r.get('acoustic') or {}; inf=inferred_acoustic(r)
 if ac.get('phase_signature')!=r.get('phase'): iss.append(issue('A-001','error','acoustic.phase_signature 與字形 phase 不一致','acoustic.phase_signature',f"改為 {r.get('phase')}"))
 if ac.get('class')!=inf: iss.append(issue('A-002','error',f"acoustic.class={ac.get('class')}，推導值為 {inf}",'acoustic.class',f'改為 {inf}'))
 if inf=='silent':
  if ac.get('source')!='NONE' or r.get('phase')!='PH16-00' or ac.get('profile_id') is not None: iss.append(issue('A-003','error','silent 必須 source=NONE、PH16-00、profile_id=null','acoustic','清除 FARHP 資料'))
 else:
  if ac.get('source')=='NONE' or not ac.get('profile_id'): iss.append(issue('A-004','error','非 silent 必須指定 FARHP 來源與 profile_id','acoustic','設定 FARHP-Y 與 profile_id'))
 if inf=='noise_dominant' and r.get('phase')!='PH16-00': iss.append(issue('A-005','warning','噪聲主導音的非零 PH16 僅作弱控制量','phase','保留但降低可靠度，或設 PH16-00'))
 if ac.get('source')=='FARHP-G' and inf in {'noise_dominant','silent'}: iss.append(issue('A-006','warning','此聲學類別不適合直接解釋為 FARHP-G','acoustic.source','改用 FARHP-Y 或 NONE'))
 if inf!='silent' and float(ac.get('confidence',0))<0.5: iss.append(issue('A-007','warning','FARHP confidence 低於 0.5，不宜作硬判定','acoustic.confidence','提高資料品質或保留為低信心度標記'))
 errs=[x for x in iss if x['severity']=='error']; warns=[x for x in iss if x['severity']=='warning']
 return {'valid':not errs,'status':'PASS' if not errs else 'FAIL','error_count':len(errs),'warning_count':len(warns),'issues':iss,'ruleset_sha256':RULESET['ruleset_sha256']}

def core_for_hash(r):
 return {k:r[k] for k in ['frame','seed_base','seed_transform','seed_variant','phonology','tone','phase','operator','transform_role','semantic','acoustic']}

def rhash(r): return hashlib.sha256(json.dumps(core_for_hash(r),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def sem_for(op, frame=None, kind=None):
 mode,n=OP_ARITY[op]
 if kind is None: kind=sorted(OP_KIND[op])[0]
 if frame is None: frame=sorted(OP_FRAMES[op])[0]
 ar={'mode':mode}
 if mode=='fixed': ar['value']=n; inputs=['Any']*n
 else: ar['min']=n; ar['max']=None; inputs=['Any']*n
 return frame,kind,{'kind':kind,'concept_id':'eml.concept:item:sample','signature':{'inputs':inputs,'output':FRAME_OUT[frame],'arity':ar}}

def mk_valid(rng, idx=0, boundary=False):
 seed=rng.choice(SEEDS)
 if boundary:
  tr='ID'; role='identity'; op='OP-NULL'; frame='SEM-META'; kind='delimiter'; phon=['ST-BOUNDARY']; tone='T0'; phase='PH16-00'; ac={'source':'NONE','class':'silent','phase_signature':phase,'profile_id':None,'confidence':1.0}
  sem={'kind':kind,'concept_id':f'eml.concept:delimiter:boundary-{idx}','signature':{'inputs':[],'output':'Meta','arity':{'mode':'fixed','value':0}}}
 else:
  # choose transform then compatible semantic kind/operator
  tr=rng.choice(TRANS)
  allowed_kinds=list(TRANS_KINDS[tr])
  kind=rng.choice(allowed_kinds)
  possible=[o for o in OPS if kind in OP_KIND[o]]
  op=rng.choice(possible)
  frame=rng.choice(sorted(OP_FRAMES[op]))
  mode,n=OP_ARITY[op]; ar={'mode':mode}; inputs=['Any']*n
  if mode=='fixed': ar['value']=n
  else: ar.update({'min':n,'max':None})
  sem={'kind':kind,'concept_id':f'eml.concept:{kind}:sample-{idx}','signature':{'inputs':inputs,'output':FRAME_OUT[frame],'arity':ar}}
  role=rng.choice(sorted(TRANS_ROLES[tr]))
  # if selected role/kind doesn't fit (should fit by kind), okay
  if tr=='ID' and role=='allographic' and rng.random()<.5: role='identity'
  onset=rng.choice([None]+ONSETS)
  # choose hu compatible
  hus=sorted(ONSET_HUS[onset]) if onset else HUS
  hu=rng.choice(hus)
  rime=rng.choice(sorted(HU_RIMES[hu]))
  if rime=='RIME-ER': onset=None; hu='HU-KAIKOU'
  tone=rng.choice(TONES)
  st=None
  candidates=[None,'ST-LONG']
  if onset is None:candidates.append('ST-ZERO')
  if rime in NASAL:candidates.append('ST-NASAL')
  if rime!='RIME-ER':candidates.append('ST-RHOTIC')
  if tone=='T0': candidates=['ST-LIGHT']
  st=rng.choice(candidates)
  phon=[x for x in [onset,hu,rime,st] if x]
  phase=rng.choice(PHASES)
  cls='mixed' if onset in MIXED else 'voiced_harmonic'
  source=rng.choice(['FARHP-Y','FARHP-G'])
  ac={'source':source,'class':cls,'phase_signature':phase,'profile_id':f'eml.farhp:profile:sample-{idx}','confidence':round(rng.uniform(.6,1),3)}
 r={'id':f'eml.empsl:glyph:case-{idx}','version':'0.4','frame':frame,'seed_base':seed,'seed_transform':tr,'seed_variant':f'{seed}@{tr}','phonology':phon,'tone':tone,'phase':phase,'operator':op,'transform_role':role,'semantic':sem,'acoustic':ac,'reading':'','gloss':'generated conformance case'}
 cert=validate(r); r['validation_certificate']=cert; r['recipe_sha256']=rhash(r); return r

def mutate(r,rng):
 x=copy.deepcopy(r); choices=['bad_hu','bad_phase','bad_arity','bad_transform','bad_light','bad_class','bad_variant','bad_frame','bad_kind','bad_concept','missing_rime','boundary_noise']
 m=rng.choice(choices)
 if m=='bad_hu':
  x['phonology']=[p for p in x['phonology'] if not p.startswith('HU-')]; x['phonology'].append('HU-CUOKOU');
  if not any(p.startswith('ONSET-') for p in x['phonology']): x['phonology'].insert(0,'ONSET-G')
  if not any(p.startswith('RIME-') for p in x['phonology']): x['phonology'].append('RIME-AI')
 elif m=='bad_phase': x['acoustic']['phase_signature']='PH16-15' if x['phase']!='PH16-15' else 'PH16-14'
 elif m=='bad_arity': x['semantic']['signature']['inputs'].append('Any')
 elif m=='bad_transform': x['transform_role']='identity' if x['seed_transform']!='ID' else 'semantic_modifier'
 elif m=='bad_light': x['tone']='T4'; x['phonology']=[p for p in x['phonology'] if not p.startswith('ST-')]+['ST-LIGHT']
 elif m=='bad_class': x['acoustic']['class']='silent' if x['acoustic']['class']!='silent' else 'mixed'
 elif m=='bad_variant': x['seed_variant']=f"{rng.choice(SEEDS)}@{x['seed_transform']}"
 elif m=='bad_frame': x['frame']='SEM-ENTITY' if x['operator']!='OP-NULL' else 'SEM-CAUSALITY'; x['semantic']['signature']['output']=FRAME_OUT[x['frame']]
 elif m=='bad_kind': x['semantic']['kind']='delimiter'
 elif m=='bad_concept': x['semantic']['concept_id']='not a stable id'
 elif m=='missing_rime': x['phonology']=[p for p in x['phonology'] if not p.startswith('RIME-')]
 elif m=='boundary_noise': x['phonology']=['ONSET-S','ST-BOUNDARY']; x['tone']='T4'; x['phase']='PH16-09'; x['acoustic']={'source':'FARHP-G','class':'noise_dominant','phase_signature':'PH16-09','profile_id':'eml.farhp:profile:bad','confidence':.3}
 x['id']=x['id']+'-mut'; cert=validate(x); x['validation_certificate']=cert; x['recipe_sha256']=rhash(x); x['_mutation']=m; return x

def mk_fuzz(rng,idx):
 seed=rng.choice(SEEDS); tr=rng.choice(TRANS); op=rng.choice(OPS); frame=rng.choice(FRAMES); kind=rng.choice(KINDS)
 mode=rng.choice(['fixed','variadic']); ar={'mode':mode};
 if mode=='fixed': ar['value']=rng.randrange(0,5)
 else: ar['min']=rng.randrange(0,3); ar['max']=None
 inputs=[rng.choice(TYPES) for _ in range(rng.randrange(0,5))]
 phon=rng.sample(ONSETS+HUS+RIMES+STRUCTS,k=rng.randrange(0,6))
 phase=rng.choice(PHASES)
 r={'id':f'eml.empsl:glyph:fuzz-{idx}','version':rng.choice(['0.4','0.3']),'frame':frame,'seed_base':seed,'seed_transform':tr,'seed_variant':f'{rng.choice(SEEDS)}@{tr}','phonology':phon,'tone':rng.choice(TONES),'phase':phase,'operator':op,'transform_role':rng.choice(ROLES),'semantic':{'kind':kind,'concept_id':rng.choice([f'eml.concept:{kind}:fuzz-{idx}','bad id']),'signature':{'inputs':inputs,'output':rng.choice(TYPES),'arity':ar}},'acoustic':{'source':rng.choice(SOURCES),'class':rng.choice(CLASSES),'phase_signature':rng.choice(PHASES),'profile_id':rng.choice([None,f'eml.farhp:profile:fuzz-{idx}']),'confidence':round(rng.random(),3)},'reading':'','gloss':'fuzz'}
 cert=validate(r); r['validation_certificate']=cert; r['recipe_sha256']=rhash(r); return r

rng=random.Random(20260731)
valid=[mk_valid(rng,i,boundary=(i%31==0)) for i in range(1024)]
invalid=[]
for i in range(1024):
 x=mutate(valid[i],rng)
 if x['validation_certificate']['valid']:
  x['semantic']['concept_id']='forced invalid id'
  x['validation_certificate']=validate(x)
  x['recipe_sha256']=rhash(x)
  x['_mutation']=x.get('_mutation','')+'+forced_bad_concept'
 invalid.append(x)
fuzz=[mk_fuzz(rng,i) for i in range(2048)]
allcases=valid+invalid+fuzz
with (ROOT/'corpus/EMPSL_legality_corpus_v0.4.jsonl').open('w',encoding='utf-8') as f:
 for i,r in enumerate(allcases):
  obj={'case_id':f'case-{i:05d}','generator':'valid' if i<1024 else 'mutated-invalid' if i<2048 else 'fuzz','expected_valid':r['validation_certificate']['valid'],'recipe':r}
  f.write(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
hits=collections.Counter(); errs=warns=valid_count=0
for r in allcases:
 c=r['validation_certificate']; valid_count+=c['valid']; errs+=c['error_count']; warns+=c['warning_count']; hits.update(x['rule_id'] for x in c['issues'])
REPORT={'spec_version':'0.4','ruleset_sha256':RULESET['ruleset_sha256'],'sample_count':len(allcases),'generated_valid_count':len(valid),'mutated_invalid_count':len(invalid),'fuzz_count':len(fuzz),'validator_valid_count':valid_count,'validator_invalid_count':len(allcases)-valid_count,'total_errors':errs,'total_warnings':warns,'rule_hit_counts':dict(sorted(hits.items())),'generator_breakdown':{}}
for g,subset in [('valid',valid),('mutated-invalid',invalid),('fuzz',fuzz)]:
 REPORT['generator_breakdown'][g]={'count':len(subset),'valid':sum(x['validation_certificate']['valid'] for x in subset),'invalid':sum(not x['validation_certificate']['valid'] for x in subset)}
(ROOT/'data/EMPSL_legality_report_v0.4.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/EMPSL_legality_report_v0.4.js').write_text('window.EMPSL_LEGALITY_REPORT='+json.dumps(REPORT,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
# curated examples: polished legal sample, generated legal cases, and invalid cases
polished={'id':'eml.empsl:glyph:light-closed','version':'0.4','frame':'SEM-ENTITY','seed_base':'ENO-07','seed_transform':'CLOSED','seed_variant':'ENO-07@CLOSED','phonology':['ONSET-G','HU-HEKOU','RIME-ANG'],'tone':'T1','phase':'PH16-05','operator':'OP-NULL','transform_role':'structural','semantic':{'kind':'item','concept_id':'eml.concept:item:physical-light','signature':{'inputs':[],'output':'Entity','arity':{'mode':'fixed','value':0}}},'acoustic':{'source':'FARHP-Y','class':'voiced_harmonic','phase_signature':'PH16-05','profile_id':'eml.farhp:profile:light-v01','confidence':0.92},'reading':'ㄍㄨㄤ','gloss':'光；具閉合語義外觀的示範詞素'}
polished['validation_certificate']=validate(polished);polished['recipe_sha256']=rhash(polished)
examples=[polished]
for i in [1,2,31]: examples.append(valid[i])
for i in range(5): examples.append(invalid[i])
(ROOT/'examples/EMPSL_legality_examples_v0.4.json').write_text(json.dumps({'spec_version':'0.4','recipes':examples},ensure_ascii=False,indent=2),encoding='utf-8')

# JSON schemas
arity_fixed={
 'type':'object','additionalProperties':False,'required':['mode','value'],
 'properties':{'mode':{'const':'fixed'},'value':{'type':'integer','minimum':0,'maximum':8}}
}
arity_variadic={
 'type':'object','additionalProperties':False,'required':['mode','min','max'],
 'properties':{'mode':{'const':'variadic'},'min':{'type':'integer','minimum':0,'maximum':8},'max':{'type':['integer','null'],'minimum':0,'maximum':32}}
}
semantic_schema={
 'type':'object','additionalProperties':False,'required':['kind','concept_id','signature'],
 'properties':{
  'kind':{'enum':KINDS},
  'concept_id':{'type':'string','pattern':IDPAT.pattern},
  'signature':{
   'type':'object','additionalProperties':False,'required':['inputs','output','arity'],
   'properties':{
    'inputs':{'type':'array','items':{'enum':TYPES},'maxItems':8},
    'output':{'enum':TYPES},
    'arity':{'oneOf':[arity_fixed,arity_variadic]}
   }
  }
 }
}
acoustic_schema={
 'type':'object','additionalProperties':False,
 'required':['source','class','phase_signature','profile_id','confidence'],
 'properties':{
  'source':{'enum':SOURCES},'class':{'enum':CLASSES},'phase_signature':{'enum':PHASES},
  'profile_id':{'type':['string','null'],'pattern':IDPAT.pattern},
  'confidence':{'type':'number','minimum':0,'maximum':1}
 }
}
issue_schema={
 'type':'object','additionalProperties':False,
 'required':['rule_id','severity','domain','message','field','suggestion'],
 'properties':{
  'rule_id':{'type':'string','pattern':'^[GPTSA]-[0-9]{3}$'},
  'severity':{'enum':['error','warning']},
  'domain':{'enum':['glyph','phonology','transform','semantics','acoustics']},
  'message':{'type':'string'},'field':{'type':'string'},'suggestion':{'type':'string'}
 }
}
certificate_schema={
 'type':'object','additionalProperties':False,
 'required':['valid','status','error_count','warning_count','issues','ruleset_sha256'],
 'properties':{
  'valid':{'type':'boolean'},'status':{'enum':['PASS','FAIL']},
  'error_count':{'type':'integer','minimum':0},'warning_count':{'type':'integer','minimum':0},
  'issues':{'type':'array','items':issue_schema},
  'ruleset_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}
 }
}
recipe_schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://evemisslab.com/spec/empsl-glyph-recipe-v0.4.schema.json',
 'title':'EMPSL Glyph Recipe v0.4','type':'object','additionalProperties':False,
 'required':['id','version','frame','seed_base','seed_transform','seed_variant','phonology','tone','phase','operator','transform_role','semantic','acoustic','validation_certificate','recipe_sha256'],
 'properties':{
  'id':{'type':'string','pattern':IDPAT.pattern},
  'version':{'const':'0.4'},
  'frame':{'enum':FRAMES},'seed_base':{'enum':SEEDS},'seed_transform':{'enum':TRANS},
  'seed_variant':{'enum':[v['id'] for v in VAR['variants']]},
  'phonology':{'type':'array','maxItems':4,'uniqueItems':True,'items':{'enum':ONSETS+HUS+RIMES+STRUCTS}},
  'tone':{'enum':TONES},'phase':{'enum':PHASES},'operator':{'enum':OPS},
  'transform_role':{'enum':ROLES},'semantic':semantic_schema,'acoustic':acoustic_schema,
  'reading':{'type':'string'},'gloss':{'type':'string'},
  'validation_certificate':certificate_schema,
  'recipe_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
  '_mutation':{'type':'string'}
 }
}
(ROOT/'spec/EMPSL_Glyph_Recipe_Spec_v0.4.schema.json').write_text(json.dumps(recipe_schema,ensure_ascii=False,indent=2),encoding='utf-8')
case_schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://evemisslab.com/spec/empsl-validation-case-v0.4.schema.json',
 'title':'EMPSL Validation Case v0.4','type':'object','additionalProperties':False,
 'required':['case_id','generator','expected_valid','recipe'],
 'properties':{
  'case_id':{'type':'string'},'generator':{'enum':['valid','mutated-invalid','fuzz']},
  'expected_valid':{'type':'boolean'},'recipe':{'type':'object'}
 }
}
(ROOT/'spec/EMPSL_Validation_Case_Spec_v0.4.schema.json').write_text(json.dumps(case_schema,ensure_ascii=False,indent=2),encoding='utf-8')
rule_item={
 'type':'object','additionalProperties':False,'required':['id','domain','severity','title','description'],
 'properties':{
  'id':{'type':'string','pattern':'^[GPTSA]-[0-9]{3}$'},
  'domain':{'enum':['glyph','phonology','transform','semantics','acoustics']},
  'severity':{'enum':['error','warning']},'title':{'type':'string'},'description':{'type':'string'}
 }
}
rule_schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://evemisslab.com/spec/empsl-rule-catalog-v0.4.schema.json',
 'title':'EMPSL Rule Catalog v0.4','type':'object','additionalProperties':False,
 'required':['spec_version','title','rule_count','rules','ruleset_sha256'],
 'properties':{
  'spec_version':{'const':'0.4'},'title':{'type':'string'},'rule_count':{'const':len(RULES)},
  'ruleset_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
  'rules':{'type':'array','minItems':len(RULES),'maxItems':len(RULES),'items':rule_item}
 }
}
(ROOT/'spec/EMPSL_Rule_Catalog_Spec_v0.4.schema.json').write_text(json.dumps(rule_schema,ensure_ascii=False,indent=2),encoding='utf-8')

# YAML spec
yaml=f'''spec_version: "0.4"
title: EMPSL Glyph Grammar and Legality Specification
ruleset_sha256: {RULESET['ruleset_sha256']}
recipe:
  identity: namespace:kind:local-id
  slots: [frame, seed_variant, phonology, tone, phase, operator]
  extensions: [transform_role, semantic, acoustic, validation_certificate]
validation_domains:
  glyph: [G-001, G-002, G-003, G-004]
  phonology: [P-001, P-002, P-003, P-004, P-005, P-006, P-007, P-008, P-009, P-010]
  transform: [T-001, T-002, T-003]
  semantics: [S-001, S-002, S-003, S-004, S-005, S-006]
  acoustics: [A-001, A-002, A-003, A-004, A-005, A-006, A-007]
certificate:
  statuses: [PASS, FAIL]
  issue_severity: [error, warning]
  pass_condition: error_count == 0
corpus:
  samples: {len(allcases)}
  valid_generator: 1024
  mutated_invalid: 1024
  fuzz: 2048
'''
(ROOT/'spec/EMPSL_Glyph_Grammar_Spec_v0.4.yaml').write_text(yaml,encoding='utf-8')

# Browser/Node grammar tables
def _conv(value):
 if isinstance(value,set): return sorted(value)
 if isinstance(value,tuple): return [_conv(x) for x in value]
 if isinstance(value,list): return [_conv(x) for x in value]
 if isinstance(value,dict): return {k:_conv(v) for k,v in value.items()}
 return value
grammar_tables={k.lower():_conv(globals()[k]) for k in ['FRAMES','SEEDS','TRANS','PHASES','OPS','ONSETS','HUS','RIMES','TONES','STRUCTS','TYPES','KINDS','ROLES','SOURCES','CLASSES','OP_ARITY','OP_KIND','OP_FRAMES','FRAME_OUT','TRANS_ROLES','TRANS_KINDS','HU_RIMES','ONSET_HUS','NOISE','MIXED','NASAL']}
(ROOT/'rules/EMPSL_grammar_tables_v0.4.json').write_text(json.dumps(grammar_tables,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'rules/EMPSL_grammar_tables_v0.4.js').write_text('window.EMPSL_GRAMMAR_TABLES='+json.dumps(grammar_tables,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
(ROOT/'examples/EMPSL_legality_examples_v0.4.js').write_text('window.EMPSL_LEGALITY_EXAMPLES='+json.dumps({'spec_version':'0.4','recipes':examples},ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')

print('generated',len(allcases),'cases')
print(json.dumps(REPORT,ensure_ascii=False,indent=2))
