import test from 'node:test';
import assert from 'node:assert/strict';
import {SessionStore} from '../session-store.mjs';
test('closing a paired session broadcasts closure, removes results and rejects late updates',()=>{
 const store=new SessionStore(),s=store.create();let event;
 s.listeners.add(view=>event=view);
 store.update(s.id,{status:'analyzing'});
 s.results=[{private:'old result'}];s.confirmedSizes={ring:8};
 store.close(s.id);
 assert.equal(event.status,'closed');assert.equal(event.results,null);assert.deepEqual(event.confirmedSizes,{});
 assert.throws(()=>store.update(s.id,{status:'result'}),/Session closed/);
 assert.throws(()=>store.update(s.id,{status:'connected',results:null}),/Session closed/);
 assert.equal(store.get(s.id).status,'closed');
 const fresh=store.create();assert.notEqual(fresh.id,s.id);assert.equal(fresh.status,'waiting');assert.equal(fresh.results,null);
 assert.equal(store.close(s.id).status,'closed');
});
test('closing an unknown session is harmless',()=>assert.equal(new SessionStore().close('missing'),null));
