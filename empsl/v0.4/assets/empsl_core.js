(function(root,factory){if(typeof module==='object'&&module.exports){module.exports=factory();}else{root.EMPSLCore=factory();}})(typeof self!=='undefined'?self:this,function(){
  function stable(value){if(Array.isArray(value))return '['+value.map(stable).join(',')+']';if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';return JSON.stringify(value);}
  function canonicalRecipe(recipe){return stable({frame:recipe.frame,seed_base:recipe.seed_base,seed_transform:recipe.seed_transform,seed_variant:recipe.seed_variant,phonology:[...(recipe.phonology||[])],tone:recipe.tone,phase:recipe.phase,operator:recipe.operator,transform_role:recipe.transform_role,semantic:recipe.semantic,acoustic:recipe.acoustic});}
  function fnv32x8(text){let out='';for(let lane=0;lane<8;lane++){let h=(0x811c9dc5^lane)>>>0;for(let i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}out+=h.toString(16).padStart(8,'0');}return out;}
  async function recipeHash(recipe){const txt=canonicalRecipe(recipe);if(globalThis.crypto&&crypto.subtle){const buf=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(txt));return [...new Uint8Array(buf)].map(x=>x.toString(16).padStart(2,'0')).join('');}return fnv32x8(txt);}
  function mapAtoms(reg){return Object.fromEntries(reg.atoms.map(a=>[a.id,a]));}
  function mapVariants(reg){return Object.fromEntries(reg.variants.map(v=>[v.id,v]));}
  function composeSvg(recipe,registry,variantRegistry,opts={}){const m=mapAtoms(registry),vm=mapVariants(variantRegistry);const b=id=>m[id]?m[id].body:'';const variant=vm[recipe.seed_variant];const seedBody=variant?(opts.rawVariant?variant.raw_body:variant.body):'';const g=(body,t)=>`<g transform="${t}">${body}</g>`;let p=[`<rect width="512" height="512" rx="36" fill="#fbf6ea"/>`,g(b(recipe.frame),'scale(2)'),g(seedBody,'translate(112 112) scale(1.125)')];const pos=[[38,292],[38,360],[106,360],[106,292]];(recipe.phonology||[]).slice(0,4).forEach((id,i)=>p.push(g(b(id),`translate(${pos[i][0]} ${pos[i][1]}) scale(0.32)`)));p.push(g(b(recipe.tone),'translate(192 18) scale(0.5)'));p.push(g(b(recipe.phase),'translate(360 48) scale(0.42)'));p.push(g(b(recipe.operator),'translate(354 352) scale(0.45)'));return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">${p.join('')}</svg>`;}
  function asSet(x){return new Set(x||[]);}  
  function classifyMarks(recipe,registry){const atoms=mapAtoms(registry),out={onset:[],four_hu:[],rime:[],structure:[],other:[]};for(const id of recipe.phonology||[]){const st=atoms[id]?.subtype;(out[st]||out.other).push(id);}return out;}
  function inferAcousticClass(recipe,registry,grammar){const c=classifyMarks(recipe,registry),onset=c.onset[0],rime=c.rime[0],st=c.structure;if(st.includes('ST-BOUNDARY'))return 'silent';const noisy=new Set([...(grammar.noise||[]),...(grammar.mixed||[])]);if(!rime)return noisy.has(onset)?'noise_dominant':'silent';if(asSet(grammar.mixed).has(onset))return 'mixed';return 'voiced_harmonic';}
  function issue(catalog,id,severity,message,field='',suggestion=''){const rule=(catalog.rules||[]).find(r=>r.id===id)||{};return {rule_id:id,severity,domain:rule.domain||'glyph',message,field,suggestion};}
  function validateRecipeV04(recipe,registry,variantRegistry,grammar,catalog){
    const issues=[],ids=new Set(registry.atoms.map(a=>a.id)),variants=mapVariants(variantRegistry),g=grammar;
    const add=(id,severity,msg,field='',suggestion='')=>issues.push(issue(catalog,id,severity,msg,field,suggestion));
    if(recipe.version!=='0.4')add('G-004','error','version 必須為 0.4','version','設為 0.4');
    for(const k of ['frame','tone','phase','operator'])if(!ids.has(recipe[k]))add('G-001','error',`未知 ${k}: ${recipe[k]}`,k,'選擇註冊表內 ID');
    for(const p of recipe.phonology||[])if(!ids.has(p))add('G-001','error',`未知 phonology: ${p}`,'phonology','移除或更換為已註冊附標');
    const v=variants[recipe.seed_variant];if(!v)add('G-001','error',`未知 seed_variant: ${recipe.seed_variant}`,'seed_variant','選擇已註冊變體');else if(v.base_seed!==recipe.seed_base||v.transform_id!==recipe.seed_transform)add('G-002','error','seed_base／seed_transform 與 seed_variant 不一致','seed_variant',`改為 ${recipe.seed_base}@${recipe.seed_transform}`);
    if((recipe.phonology||[]).length>4)add('G-003','error','phonology 超過四個附標','phonology','每類只保留一個');
    const c=classifyMarks(recipe,registry);if(new Set(recipe.phonology||[]).size!==(recipe.phonology||[]).length||['onset','four_hu','rime','structure'].some(k=>c[k].length>1))add('P-001','error','音系附標重複或同類別超過一個','phonology','每類只保留一個');
    const onset=c.onset[0],hu=c.four_hu[0],rime=c.rime[0],st=c.structure[0];
    if(onset&&hu&&!asSet(g.onset_hus[onset]).has(hu))add('P-002','error',`${onset} 不接受 ${hu}`,'phonology','更換四呼或聲母');
    if(hu&&rime&&!asSet(g.hu_rimes[hu]).has(rime))add('P-003','error',`${hu} 不接受 ${rime}`,'phonology','更換韻類');
    if(rime==='RIME-ER'&&(onset||(hu&&hu!=='HU-KAIKOU')||st==='ST-RHOTIC'))add('P-004','error','RIME-ER 只允許零聲母開口呼，且不可再加 ST-RHOTIC','phonology','移除聲母／兒化附標並改用開口呼');
    if(recipe.tone==='T0'&&st!=='ST-LIGHT')add('P-005','warning','T0 建議加入 ST-LIGHT','tone','加入 ST-LIGHT');
    if(st==='ST-LIGHT'&&recipe.tone!=='T0')add('P-005','error','ST-LIGHT 必須使用 T0','tone','將聲調改為 T0');
    if(st==='ST-NASAL'&&!asSet(g.nasal).has(rime))add('P-006','error','ST-NASAL 需要 AN／EN／ANG／ENG','phonology','更換鼻韻或移除 ST-NASAL');
    if(st==='ST-ZERO'&&onset)add('P-007','error','ST-ZERO 不可與聲母共現','phonology','移除聲母');
    if(st==='ST-BOUNDARY'&&(onset||hu||rime||recipe.tone!=='T0'||recipe.phase!=='PH16-00'))add('P-008','error','ST-BOUNDARY 必須排他並使用 T0／PH16-00','phonology','清除聲母四呼韻類，設 T0 與 PH16-00');
    if(st==='ST-RHOTIC'&&rime==='RIME-ER')add('P-009','error','兒化不得與 RIME-ER 重複編碼','phonology','保留其中一種兒化表示');
    if(st!=='ST-BOUNDARY'&&!rime)add('P-010','error','非邊界詞素缺少韻類','phonology','加入 RIME-*');
    if(hu&&!rime)add('P-010','error','四呼不可沒有韻類','phonology','加入相容韻類');
    const sem=recipe.semantic||{},kind=sem.kind,op=recipe.operator,role=recipe.transform_role,tr=recipe.seed_transform;
    if(!asSet(g.trans_roles[tr]).has(role))add('T-001','error',`${tr} 不接受 transform_role=${role}`,'transform_role',`改為 ${(g.trans_roles[tr]||[])[0]||'identity'}`);
    if(!asSet(g.trans_kinds[tr]).has(kind))add('T-002','error',`${tr} 不適用於 semantic.kind=${kind}`,'semantic.kind','更換變換或語義種類');
    if((kind==='delimiter'||st==='ST-BOUNDARY')&&tr!=='ID')add('T-003','error','邊界／delimiter 只能使用 ID 變換','seed_transform','設為 ID');
    const idpat=/^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*:[a-z][a-z0-9_-]*:[0-9a-z_-]+$/;
    if(!idpat.test(sem.concept_id||''))add('S-001','error','concept_id 不符合三段式穩定 ID','semantic.concept_id','使用 eml.concept:item:local-id 格式');
    if(!asSet(g.op_kind[op]).has(kind))add('S-002','error',`${op} 不接受 semantic.kind=${kind}`,'semantic.kind','更換 semantic.kind 或 operator');
    const ar=sem.signature?.arity||{},inputs=sem.signature?.inputs||[],expected=g.op_arity[op];
    if(expected){const [mode,n]=expected;if(ar.mode!==mode)add('S-003','error',`${op} 需要 arity.mode=${mode}`,'semantic.signature.arity','修正參數模式');if(mode==='fixed'){if(ar.value!==n)add('S-003','error',`${op} 需要 fixed arity=${n}`,'semantic.signature.arity.value',`設為 ${n}`);if(inputs.length!==n)add('S-004','error',`inputs 長度 ${inputs.length} 與 arity ${n} 不符`,'semantic.signature.inputs',`提供 ${n} 個輸入型別`);}else if((ar.min??-1)<n)add('S-003','error',`${op} 需要 variadic min>=${n}`,'semantic.signature.arity.min',`設為 ${n}`);}
    if(!asSet(g.op_frames[op]).has(recipe.frame))add('S-005','error',`${op} 不適用於 ${recipe.frame}`,'frame','選擇相容外框');
    const out=sem.signature?.output,expout=g.frame_out[recipe.frame];if(out&&expout&&out!==expout)add('S-006','warning',`輸出型別 ${out} 與外框建議 ${expout} 不同`,'semantic.signature.output',`改為 ${expout} 或記錄偏離理由`);
    const ac=recipe.acoustic||{},inf=inferAcousticClass(recipe,registry,g);
    if(ac.phase_signature!==recipe.phase)add('A-001','error','acoustic.phase_signature 與字形 phase 不一致','acoustic.phase_signature',`改為 ${recipe.phase}`);
    if(ac.class!==inf)add('A-002','error',`acoustic.class=${ac.class}，推導值為 ${inf}`,'acoustic.class',`改為 ${inf}`);
    if(inf==='silent'){if(ac.source!=='NONE'||recipe.phase!=='PH16-00'||ac.profile_id!==null)add('A-003','error','silent 必須 source=NONE、PH16-00、profile_id=null','acoustic','清除 FARHP 資料');}
    else if(ac.source==='NONE'||!ac.profile_id)add('A-004','error','非 silent 必須指定 FARHP 來源與 profile_id','acoustic','設定 FARHP-Y 與 profile_id');
    if(inf==='noise_dominant'&&recipe.phase!=='PH16-00')add('A-005','warning','噪聲主導音的非零 PH16 僅作弱控制量','phase','保留但降低可靠度，或設 PH16-00');
    if(ac.source==='FARHP-G'&&(inf==='noise_dominant'||inf==='silent'))add('A-006','warning','此聲學類別不適合直接解釋為 FARHP-G','acoustic.source','改用 FARHP-Y 或 NONE');
    if(inf!=='silent'&&Number(ac.confidence??0)<0.5)add('A-007','warning','FARHP confidence 低於 0.5，不宜作硬判定','acoustic.confidence','提高資料品質或保留為低信心度標記');
    const errors=issues.filter(x=>x.severity==='error'),warnings=issues.filter(x=>x.severity==='warning');return {valid:errors.length===0,status:errors.length?'FAIL':'PASS',error_count:errors.length,warning_count:warnings.length,issues,ruleset_sha256:catalog.ruleset_sha256};
  }
  function autoRepair(recipe,registry,variantRegistry,grammar,catalog){
    const r=JSON.parse(JSON.stringify(recipe)),g=grammar,atoms=mapAtoms(registry);r.version='0.4';r.seed_variant=`${r.seed_base}@${r.seed_transform}`;
    const seen=new Set(),keep={};for(const id of r.phonology||[]){if(seen.has(id))continue;seen.add(id);const st=atoms[id]?.subtype;if(['onset','four_hu','rime','structure'].includes(st)&&!keep[st])keep[st]=id;}r.phonology=['onset','four_hu','rime','structure'].map(k=>keep[k]).filter(Boolean);
    let c=classifyMarks(r,registry),st=c.structure[0];
    if(st==='ST-BOUNDARY'||r.semantic?.kind==='delimiter'){
      r.seed_transform='ID';r.seed_variant=`${r.seed_base}@ID`;r.transform_role='identity';r.phonology=['ST-BOUNDARY'];r.tone='T0';r.phase='PH16-00';r.operator='OP-NULL';r.frame='SEM-META';r.semantic={kind:'delimiter',concept_id:/^[a-z]/.test(r.semantic?.concept_id||'')?r.semantic.concept_id:'eml.concept:delimiter:boundary',signature:{inputs:[],output:'Meta',arity:{mode:'fixed',value:0}}};r.acoustic={source:'NONE',class:'silent',phase_signature:'PH16-00',profile_id:null,confidence:1};
    }else{
      c=classifyMarks(r,registry);let onset=c.onset[0],hu=c.four_hu[0]||'HU-KAIKOU',rime=c.rime[0]||'RIME-A',structure=c.structure[0];if(onset&&!asSet(g.onset_hus[onset]).has(hu))hu=(g.onset_hus[onset]||['HU-KAIKOU'])[0];if(!asSet(g.hu_rimes[hu]).has(rime))rime=(g.hu_rimes[hu]||['RIME-A'])[0];if(rime==='RIME-ER'){onset=null;hu='HU-KAIKOU';if(structure==='ST-RHOTIC')structure=null;}if(structure==='ST-ZERO')onset=null;if(structure==='ST-NASAL'&&!asSet(g.nasal).has(rime))structure=null;if(r.tone==='T0')structure='ST-LIGHT';else if(structure==='ST-LIGHT')structure=null;r.phonology=[onset,hu,rime,structure].filter(Boolean);
      const roles=g.trans_roles[r.seed_transform]||['identity'];if(!roles.includes(r.transform_role))r.transform_role=roles[0];
      const op=r.operator,allowedKinds=g.op_kind[op]||['item'],transformKinds=g.trans_kinds[r.seed_transform]||allowedKinds;let kinds=allowedKinds.filter(k=>transformKinds.includes(k));if(!kinds.length){r.seed_transform='ID';r.seed_variant=`${r.seed_base}@ID`;r.transform_role='identity';kinds=allowedKinds;}if(!kinds.includes(r.semantic?.kind))r.semantic={...(r.semantic||{}),kind:kinds[0]};
      const frames=g.op_frames[op]||[r.frame];if(!frames.includes(r.frame))r.frame=frames[0];const [mode,n]=g.op_arity[op]||['fixed',0];const sig={inputs:Array(n).fill('Any'),output:g.frame_out[r.frame]||'Any',arity:mode==='fixed'?{mode,value:n}:{mode,min:n,max:null}};r.semantic={kind:r.semantic.kind,concept_id:/^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*:[a-z][a-z0-9_-]*:[0-9a-z_-]+$/.test(r.semantic?.concept_id||'')?r.semantic.concept_id:`eml.concept:${r.semantic.kind}:repaired`,signature:sig};
      const cls=inferAcousticClass(r,registry,g);r.acoustic={source:cls==='silent'?'NONE':(r.acoustic?.source==='FARHP-G'?'FARHP-G':'FARHP-Y'),class:cls,phase_signature:r.phase,profile_id:cls==='silent'?null:(r.acoustic?.profile_id||'eml.farhp:profile:repaired'),confidence:Math.max(0,Math.min(1,Number(r.acoustic?.confidence??0.8)))};
    }
    r.validation_certificate=validateRecipeV04(r,registry,variantRegistry,grammar,catalog);return r;
  }
  function upgradeV03(recipe,registry,variantRegistry,grammar,catalog){const r={...recipe,version:'0.4',transform_role:recipe.seed_transform==='ID'?'identity':'allographic',semantic:{kind:recipe.operator==='OP-NULL'?'item':'operator',concept_id:recipe.concept_id||'eml.concept:item:upgraded',signature:{inputs:[],output:grammar.frame_out[recipe.frame]||'Any',arity:{mode:'fixed',value:0}}},acoustic:{source:'FARHP-Y',class:'voiced_harmonic',phase_signature:recipe.phase,profile_id:'eml.farhp:profile:upgraded',confidence:0.5}};return autoRepair(r,registry,variantRegistry,grammar,catalog);}
  return {stable,canonicalRecipe,recipeHash,composeSvg,classifyMarks,inferAcousticClass,validateRecipeV04,autoRepair,upgradeV03};
});
