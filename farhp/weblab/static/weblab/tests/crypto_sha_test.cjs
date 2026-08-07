'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const code=fs.readFileSync(require('path').join(__dirname,'..','app.js'),'utf8');
const context=vm.createContext({console,Math,Number,Array,ArrayBuffer,DataView,Float32Array,Float64Array,Uint8Array,TextEncoder,Blob,Date,JSON,setTimeout,clearTimeout,crypto:require('crypto').webcrypto,document:{querySelector:()=>null,querySelectorAll:()=>[],addEventListener:()=>{}},window:{},localStorage:{getItem:()=>null,setItem:()=>{}},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},location:{hash:''},requestAnimationFrame:()=>0});
vm.runInContext(code,context,{filename:'app.js'});
(async()=>{
 const fp=await vm.runInContext("planFingerprint({study:'FARHP',version:'0.8'})",context);
 assert.strictEqual(fp.algorithm,'SHA-256');assert.match(fp.value,/^[0-9a-f]{64}$/);
 const p=await vm.runInContext("participantPseudonym('S','P')",context);assert.match(p,/^PID-[0-9a-f]{20}$/);
 console.log('FARHP WebLab WebCrypto test: PASS');
})().catch(e=>{console.error(e);process.exit(1)});
