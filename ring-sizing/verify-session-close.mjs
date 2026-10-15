import assert from 'node:assert/strict';
const base='http://127.0.0.1:4173';
const create=async()=>{const r=await fetch(base+'/api/sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"lang":"fr"}'});assert.equal(r.status,201);return r.json();};
const old=await create();
const ac=new AbortController();
try{
 const stream=await fetch(`${base}/api/sessions/${old.id}/events`,{signal:ac.signal});const reader=stream.body.getReader();
 assert.match(new TextDecoder().decode((await reader.read()).value),/waiting/);
 const closed=await fetch(`${base}/api/sessions/${old.id}`,{method:'DELETE'});assert.equal((await closed.json()).status,'closed');
 assert.match(new TextDecoder().decode((await reader.read()).value),/closed/);
 const late=await fetch(`${base}/api/sessions/${old.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:'{"status":"connected"}'});assert.equal(late.status,400);
 const photo=await fetch(`${base}/api/sessions/${old.id}/analyze`,{method:'POST',body:'ignored'});assert.equal(photo.status,410);
 const fresh=await create();assert.notEqual(fresh.id,old.id);assert.equal(fresh.status,'waiting');await fetch(`${base}/api/sessions/${fresh.id}`,{method:'DELETE'});
 console.log('Live reset verified: phone SSE receives closure; old session rejects updates and photos; fresh QR session is waiting.');
}finally{ac.abort();}
