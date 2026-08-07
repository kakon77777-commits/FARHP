'use strict';
const {execFileSync}=require('child_process');const path=require('path');
const presets=['grouped','yitianbuqu','yigebuhaoma','wohenhao','nihaoma','mamahao','nihao'];
for(const preset of presets){console.log('Generating',preset);execFileSync(process.execPath,[path.join(__dirname,'generate_one_utterance.cjs'),preset],{stdio:'inherit',timeout:120000});}
console.log(`Generated ${presets.length} utterance WAV/JSON pairs.`);
