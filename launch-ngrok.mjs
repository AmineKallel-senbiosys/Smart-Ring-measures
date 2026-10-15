import {spawn} from 'node:child_process';
import process from 'node:process';
import {readFile} from 'node:fs/promises';
// Repository token configuration, outside the web server's dist directory.
const config=JSON.parse(await readFile(new URL('./ring-sizing/ngrok-local.config.json',import.meta.url),'utf8'));
const token=typeof config.authtoken==='string'?config.authtoken.trim():'';
if(!token)throw new Error('Missing authtoken in ngrok-local.config.json');
const child=spawn('ngrok',['http','http://127.0.0.1:4173','--log=stdout','--log-format=json'],{windowsHide:true,env:{...process.env,NGROK_AUTHTOKEN:token},stdio:['ignore','pipe','pipe']});
let diagnostic='';
for(const output of [child.stdout,child.stderr])output.on('data',chunk=>{diagnostic=(diagnostic+chunk.toString().split(token).join('[redacted]')).slice(-6000);});
child.on('error',e=>console.log('ngrok could not start: '+e.code));
child.on('exit',code=>{console.log('ngrok stopped with exit code '+code);console.log(diagnostic);process.exit(code||0);});
for(let i=0;i<60;i++){
  try{const r=await fetch('http://127.0.0.1:4040/api/tunnels');const data=await r.json();const tunnel=data.tunnels.find(x=>x.proto==='https'&&x.config.addr.includes('4173'));if(tunnel){console.log(JSON.stringify({url:tunnel.public_url,ngrok_pid:child.pid}));break;}}
  catch{}
  await new Promise(r=>setTimeout(r,500));
  if(i===59)console.log('Tunnel not ready yet. '+diagnostic);
}
process.on('SIGINT',()=>{child.kill();process.exit(0);});
