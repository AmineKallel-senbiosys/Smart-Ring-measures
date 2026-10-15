import {mkdir,writeFile,readdir} from 'node:fs/promises';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
const root=path.resolve('../test');
const groups=new Map();let allocation=Promise.resolve();
export function allocateTestFolder(sessionId,testId,mode,auditRoot=root){
 const operation=allocation.then(async()=>{
  await mkdir(auditRoot,{recursive:true});
  const key=auditRoot+'|'+sessionId+'|'+(testId||'legacy');
  let group=groups.get(key);
  if(!group){
   const entries=await readdir(auditRoot);let number=1+Math.max(0,...entries.map(name=>Number(/^Test N(\d+)$/.exec(name)?.[1]||0)));
   for(;;number++){const folder=path.join(auditRoot,'Test N'+number);try{await mkdir(folder);group={folder,number};break;}catch(error){if(error.code!=='EEXIST')throw error;}}
   groups.set(key,group);
   await writeFile(path.join(group.folder,'test-info.json'),JSON.stringify({testNumber:group.number,sessionId,testId:testId||null,startedAt:new Date().toISOString()},null,2));
  }
  if(!testId&&mode==='analyze')groups.delete(key);
  return group;
 });
 allocation=operation.catch(()=>{});return operation;
}
export async function beginScanAudit(sessionId,image,mode,contentType,context={}){
 if(process.env.RING_TEST_CAPTURE==='0')return async()=>{};
 const startedAt=new Date().toISOString(),started=Date.now();
 let group;try{group=await allocateTestFolder(sessionId,context.testId,mode);}catch{console.error('Could not create numbered scan test folder.');return async()=>{};}
 const folder=path.join(group.folder,startedAt.replace(/[:.]/g,'-')+'-'+mode+'-'+randomUUID().slice(0,8));
 const extension=contentType==='image/png'?'png':'jpg';
 const base={testNumber:group.number,sessionId,mode,startedAt,inputBytes:image.length,contentType,context};
 try{await mkdir(folder,{recursive:true});await writeFile(path.join(folder,'input.'+extension),image);await writeFile(path.join(folder,'report.json'),JSON.stringify({...base,status:'processing'},null,2));}
 catch{console.error('Could not write local scan test files.');return async()=>{};}
 return async packet=>{try{
  if(packet.worker?.annotatedImageBase64){
   const {annotatedImageBase64,...worker}=packet.worker;
   await writeFile(path.join(folder,'measurements.jpg'),Buffer.from(annotatedImageBase64,'base64'));
   packet={...packet,worker,annotatedImage:'measurements.jpg'};
  }
  if(packet.worker?.debug)await writeFile(path.join(folder,'finger-measurements.json'),JSON.stringify(packet.worker.debug,null,2));
  await writeFile(path.join(folder,'report.json'),JSON.stringify({...base,finishedAt:new Date().toISOString(),durationMs:Date.now()-started,...packet},null,2));
 }catch{console.error('Could not finish local scan test report.');}};
}
