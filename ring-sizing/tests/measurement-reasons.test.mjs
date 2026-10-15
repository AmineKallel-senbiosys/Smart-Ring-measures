import test from 'node:test';
import assert from 'node:assert/strict';
import {SessionStore} from '../session-store.mjs';
import {resultWithAdjustedTable} from '../dist/table-adjustment.mjs';
test('paired viewers retain a failed finger reason without turning failed guesses into circumference',()=>{
 const store=new SessionStore(),s=store.create();let event;s.listeners.add(v=>event=v);
 store.update(s.id,{results:['little','ring','middle','index'].map((finger,i)=>i===0?{finger,measured:false,circumference:90,failureReason:'inconsistent-widths'}:{finger,diameter:18,widthMm:18,circumference:56.5,quality:80})});
 assert.equal(event.results[0].failureReason,'inconsistent-widths');assert.equal(event.results[0].circumference,null);assert.equal(event.results[0].size,null);
});
test('measurable circumference below table minimum is kept with no matching size',()=>{
 const store=new SessionStore(),s=store.create();store.update(s.id,{results:['little','ring','middle','index'].map(finger=>({finger,diameter:49/Math.PI,widthMm:49/Math.PI,circumference:49,quality:80}))});
 const result=resultWithAdjustedTable(store.view(s).results[0],2);
 assert.equal(result.circumference,49);assert.equal(result.measured,true);assert.equal(result.size,null);assert.equal(result.outOfRange,true);assert.equal(result.quality,80);
});

test('circumference above maximum remains visible without a product size',()=>{
 const store=new SessionStore(),s=store.create();store.update(s.id,{results:['little','ring','middle','index'].map(finger=>({finger,diameter:70/Math.PI,widthMm:70/Math.PI,circumference:70,quality:80}))});
 const r=store.view(s).results[0];assert.equal(r.circumference,70);assert.equal(r.size,null);assert.equal(r.outOfRange,true);assert.equal(r.measured,true);
});
