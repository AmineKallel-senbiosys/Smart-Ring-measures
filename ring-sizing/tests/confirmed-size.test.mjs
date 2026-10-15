import test from 'node:test';
import assert from 'node:assert/strict';
import {SessionStore} from '../session-store.mjs';
test('confirmed sizes sync without altering table estimates and clear on repeat',()=>{
 const store=new SessionStore(),s=store.create();let event;s.listeners.add(v=>event=v);
 store.update(s.id,{results:['little','ring','middle','index'].map(finger=>({finger,diameter:18,widthMm:18,circumference:56.5,quality:83})),status:'result'});
 store.update(s.id,{confirmedSize:{finger:'little',size:6}});
 assert.equal(event.confirmedSizes.little,6);assert.equal(event.results[0].size,8);assert.equal(event.results[0].circumference,56.5);assert.equal(event.results[0].quality,83);
 assert.throws(()=>store.update(s.id,{confirmedSize:{finger:'little',size:7}}));
 store.update(s.id,{correction:{finger:'little',circumference:62}});assert.equal(event.confirmedSizes.little,6);assert.equal(event.results[0].size,10);
 store.update(s.id,{results:null});assert.deepEqual(event.confirmedSizes,{});
});
