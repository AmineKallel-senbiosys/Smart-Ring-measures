import test from 'node:test';
import assert from 'node:assert/strict';
import {SessionStore} from '../session-store.mjs';
test('automatic results retain measured fingers and never size unmeasured guides',()=>{
 const store=new SessionStore(),session=store.create();let event;session.listeners.add(s=>event=s);
 const results=['little','ring','middle','index'].map((finger,i)=>i===1?{finger,measured:false,size:8,circumference:99,quality:95}:{finger,diameter:18,circumference:56.5,widthMm:18,quality:83});
 store.update(session.id,{status:'result',results});assert.equal(event.status,'result');assert.equal(event.results[1].size,null);assert.equal(event.results[1].circumference,null);assert.equal(event.results[1].quality,0);assert.equal(event.results[0].size,8);assert.equal(event.results[0].quality,83);
 store.update(session.id,{correction:{finger:'ring',circumference:56.5}});assert.equal(session.results[1].measured,true);assert.equal(session.results[1].size,8);assert.equal(session.results[1].quality,0);
});
