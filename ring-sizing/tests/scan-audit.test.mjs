import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {allocateTestFolder} from '../scan-audit.mjs';

test('scan attempts share numbered folders and numbering resumes without collisions',async()=>{
 const root=await mkdtemp(path.join(os.tmpdir(),'ring-audit-numbering-'));
 await mkdir(path.join(root,'Test N4'));
 const [first,repeat,second]=await Promise.all([
  allocateTestFolder('session','attempt-a','inspect',root),
  allocateTestFolder('session','attempt-a','analyze',root),
  allocateTestFolder('session','attempt-b','inspect',root)
 ]);
 assert.equal(first.number,5);assert.equal(first.folder,repeat.folder);assert.equal(second.number,6);
 const info=JSON.parse(await readFile(path.join(first.folder,'test-info.json'),'utf8'));
 assert.equal(info.testId,'attempt-a');
 const legacy=await allocateTestFolder('old-session',null,'inspect',root);
 assert.equal((await allocateTestFolder('old-session',null,'analyze',root)).folder,legacy.folder);
 assert.equal((await allocateTestFolder('old-session',null,'inspect',root)).number,legacy.number+1);
});
