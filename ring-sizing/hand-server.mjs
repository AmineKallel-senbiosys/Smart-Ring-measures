import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {SessionStore} from './session-store.mjs';
import {measure} from './vision-worker.mjs';
import {beginScanAudit} from './scan-audit.mjs';
const root=path.resolve('dist'),sessions=new SessionStore();
setInterval(()=>{for(const id of sessions.sessions.keys())sessions.get(id);},60000).unref();
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.wasm':'application/wasm','.task':'application/octet-stream','.jpg':'image/jpeg','.png':'image/png'};
const json=(res,status,data)=>res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'}).end(JSON.stringify(data));
async function body(req){let data='';for await(const chunk of req){data+=chunk;if(data.length>16000)throw new Error('Request too large');}return JSON.parse(data||'{}');}
http.createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');let p=decodeURIComponent(url.pathname);
 if(p==='/api/sessions'&&req.method==='POST'){const s=sessions.create((await body(req)).lang);return json(res,201,sessions.view(s));}
 const analysis=p.match(/^\/api\/sessions\/([a-z0-9-]+)\/analyze$/);
 if(analysis&&req.method==='POST'){
  const s=sessions.get(analysis[1]);if(!s)return json(res,404,{error:'Session expired'});if(s.status==='closed')return json(res,410,{error:'Session closed. Scan the new QR code.'});
  const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>4*1024*1024)return json(res,413,{error:'Photo is too large'});chunks.push(chunk);}
  const inspect=url.searchParams.has('inspect'),image=Buffer.concat(chunks),context={};
  try{const supplied=JSON.parse(req.headers['x-scan-context']||'{}');if(typeof supplied.testId==='string'&&/^[a-f0-9-]{36}$/.test(supplied.testId))context.testId=supplied.testId;for(const key of ['sourceWidth','sourceHeight','sentWidth','sentHeight','previewWidth','previewHeight'])if(Number.isFinite(supplied[key])&&supplied[key]>=0&&supplied[key]<=20000)context[key]=supplied[key];}catch{}
  const finishAudit=await beginScanAudit(s.id,image,inspect?'inspect':'analyze',req.headers['content-type'],context);
  try{
   if(!inspect)sessions.update(s.id,{status:'analyzing',stage:0,results:null});
   const result=await measure(image,inspect?'inspect':'analyze',stage=>{if(!inspect&&s.status!=='closed')sessions.update(s.id,{stage});});
   if(s.status==='closed'){await finishAudit({status:'cancelled',reason:'Session closed during analysis'});return json(res,410,{error:'Session closed. Scan the new QR code.'});}
   if(!inspect)sessions.update(s.id,{status:'result',results:result.results,selectedFinger:0});
   const response=inspect?result:{results:sessions.view(s).results,method:result.review.method};
   await finishAudit({status:'success',worker:result,response});return json(res,200,response);
  }catch(e){if(!inspect&&s.status!=='closed')sessions.update(s.id,{status:'error'});await finishAudit({status:'error',error:e.message});return json(res,422,{error:e.message});}
 }
 const match=p.match(/^\/api\/sessions\/([a-z0-9-]+)(\/events)?$/);
 if(match){const s=sessions.get(match[1]);if(!s)return json(res,404,{error:'Session expired. Scan a new QR code.'});
 if(match[2]&&req.method==='GET'){res.writeHead(200,{'Content-Type':'text/event-stream','Cache-Control':'no-cache','Connection':'keep-alive','X-Accel-Buffering':'no'});const send=data=>res.write(`data: ${JSON.stringify(data)}\n\n`);send(sessions.view(s));s.listeners.add(send);const heartbeat=setInterval(()=>res.write(': heartbeat\n\n'),15000);req.on('close',()=>{clearInterval(heartbeat);s.listeners.delete(send);});return;}
 if(req.method==='DELETE')return json(res,200,sessions.view(sessions.close(s.id)));if(req.method==='GET')return json(res,200,sessions.view(s));if(req.method==='PATCH'){try{return json(res,200,sessions.view(sessions.update(s.id,await body(req))));}catch(e){return json(res,400,{error:e.message});}}return json(res,405,{error:'Method not allowed'});}
 if(p==='/'||p.endsWith('/pages/online-sizing'))p='/index.html';const file=path.resolve(root,'.'+p);if(!file.startsWith(root+path.sep))return res.writeHead(403).end();const content=await readFile(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':p.startsWith('/vision/')?'public,max-age=86400':'no-store','X-Content-Type-Options':'nosniff'}).end(content);
 }catch{res.writeHead(404).end('Not found');}}).listen(4173,'0.0.0.0',()=>console.log('Local: http://localhost:4173'));

