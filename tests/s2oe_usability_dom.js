// Neutral DOM projection checks; no browser, network or video playback.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('tools/s2oe_player.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};
function element(id){return elements[id]??=(id==='video'?{controls:true,pause(){this.paused=true},addEventListener(){}}:{textContent:''})}
let requests=0;
const context={document:{getElementById:element},setTimeout(){return 1},clearTimeout(){},
    fetch(){requests++;return new Promise(()=>{})}};
vm.createContext(context);vm.runInContext(script,context);
const state={phase:'RUNNING',completed:8,total:24,source:'neutral',current:{ordinal:9},
    last_processed:{pass_number:1,media_start_seconds:3.5,kind:'COMPLETE_AV_PERCEPTION',runtime_window:[1,2]},
    closure_cause:'UNKNOWN',last:{perception:'RECORDED',memory:'COMMITTED',context:'NOT_REQUESTED'}};
const before=JSON.stringify(state);
context.render(state);
assert.equal(elements.video.controls,false);assert.equal(elements.video.paused,true);
assert.equal(elements.phase.textContent,'Verarbeitung läuft');
assert(elements.window.textContent.includes('3.5–3.6'));assert(!elements.window.textContent.includes('undefined'));
assert.equal(JSON.stringify(state),before);
context.render({...state,phase:'NOT_EVALUABLE',closure_cause:'USER_STOP',session_failure:'INCOMPLETE'});
assert.equal(elements.phase.textContent,'Unvollständig: 8/24 Ereignisse');
assert.equal(elements.cause.textContent,'Benutzer-Stopp');assert.equal(elements.error.textContent,'INCOMPLETE');
for(const [cause,label] of Object.entries({SERVER_SHUTDOWN:'Serverbeendigung',SOURCE_END:'Quellenende',TECHNICAL_ERROR:'Technischer Fehler',UNKNOWN:'Ursache unbekannt'})){
    context.render({...state,phase:'NOT_EVALUABLE',closure_cause:cause});assert.equal(elements.cause.textContent,label);
}
context.render({...state,phase:'RECORDING_COMPLETE',completed:24,closure_cause:'COMPLETED'});
assert.equal(elements.phase.textContent,'Vollständig verarbeitet');
assert.equal(requests,1); // Initial status only, never POST/start.
console.log('DOM_OK');
