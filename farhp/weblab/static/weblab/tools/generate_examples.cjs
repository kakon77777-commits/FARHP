'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.join(__dirname,'..');
const code=fs.readFileSync(path.join(root,'app.js'),'utf8');
const context=vm.createContext({console,Math,Number,Array,ArrayBuffer,DataView,Float32Array,Float64Array,Uint8Array,Blob,Date,JSON,setTimeout,clearTimeout,
 document:{querySelector:()=>null,querySelectorAll:()=>[],addEventListener:()=>{}},window:{},localStorage:{getItem:()=>null,setItem:()=>{}},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},location:{hash:''},requestAnimationFrame:()=>0});
vm.runInContext(code,context,{filename:'app.js'});
const ev=x=>vm.runInContext(x,context);
ev(`Object.assign(state,{f0:125,duration:.8,K:24,anchor:.35,gain:.8,vowel:'a',phasePreset:'curved',strength:1,quantM:16});
state.amplitudes=makeAmplitudes('a',24,125);state.basePhase=new Array(24).fill(0);state.targetPhase=phasePreset('curved',24);state.phase=state.targetPhase.slice();`);
function wavBuffer(samples,sr){
 const b=Buffer.alloc(44+samples.length*2);b.write('RIFF',0);b.writeUInt32LE(36+samples.length*2,4);b.write('WAVE',8);b.write('fmt ',12);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(1,22);b.writeUInt32LE(sr,24);b.writeUInt32LE(sr*2,28);b.writeUInt16LE(2,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(samples.length*2,40);
 let o=44;for(const x of samples){b.writeInt16LE(Math.round(Math.max(-1,Math.min(1,x))*32767),o);o+=2;}return b;
}
const out=path.join(root,'examples','mandarin_tones');fs.mkdirSync(out,{recursive:true});
for(const tone of [1,2,3,4,0]){
 ev(`Object.assign(syllableState,{initial:'ㄇ',final:'a',tone:${tone},baseF0:132,duration:.78,residualStrength:.52,phaseStrength:1,phaseSource:'curved'});`);
 const data=ev(`(()=>{const r=synthesizeSyllable();return {samples:Array.from(r.samples),manifest:syllableManifest()};})()`);
 fs.writeFileSync(path.join(out,`ma_tone${tone}.wav`),wavBuffer(data.samples,24000));
 fs.writeFileSync(path.join(out,`ma_tone${tone}.json`),JSON.stringify(data.manifest,null,2));
}
console.log('Generated Mandarin tone gallery: 5 WAV + 5 JSON');
