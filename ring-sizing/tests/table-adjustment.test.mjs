import test from 'node:test';
import assert from 'node:assert/strict';
import {BASE_FIT,adjustedFitTable,resultWithAdjustedTable} from '../dist/table-adjustment.mjs';
test('adjusting thresholds preserves circumference and quality while changing table decision',()=>{
 const original={finger:'little',measured:true,circumference:55,widthMm:17.5,photoCircumference:55,quality:83,size:8,zone:'loose'};
 const next=resultWithAdjustedTable(original,2);
 assert.equal(next.size,6);assert.equal(next.zone,'tight');
 for(const field of ['circumference','photoCircumference','widthMm','quality'])assert.equal(next[field],original[field]);
 assert.equal(original.size,8);
 assert.equal(adjustedFitTable(2)[0].min,50.6*1.02);
 assert.equal(adjustedFitTable(-2)[0].min,50.6*.98);
 assert.equal(BASE_FIT[0].min,50.6);
});
test('all scaled boundaries retain loose OK tight inclusivity and adjacent sizes',()=>{
 for(const percent of [-4,-3,-2,-1,0,1,2,3,4]){
  const rows=adjustedFitTable(percent);
  for(const row of rows){
   const classify=c=>resultWithAdjustedTable({finger:'little',circumference:c},percent);
   assert.equal(classify(row.min).size,row.size);
   assert.equal(classify(row.okMin-.000001).zone,'loose');
   assert.equal(classify(row.okMin).zone,'ok');assert.equal(classify(row.okMax).zone,'ok');
   assert.equal(classify(row.okMax+.000001).zone,row.maxInclusive===undefined?'tight':'out-of-range');
   if(row.maxEx!==null){assert.equal(classify(row.maxEx-.000001).size,row.size);assert.equal(classify(row.maxEx).size,row.size+2);}
  }
  assert.equal(resultWithAdjustedTable({finger:'little',circumference:rows[0].min-.000001},percent).outOfRange,true);
  assert.equal(resultWithAdjustedTable({finger:'little',circumference:rows.at(-1).maxInclusive+.000001},percent).size,null);
 }
 const failed={measured:false,circumference:null,quality:0};assert.equal(resultWithAdjustedTable(failed,2),failed);
});

test('little-finger adjustment never changes the other three fingers',()=>{
 for(const percent of [-4,-3,-2,-1,1,2,3,4]){
  for(const finger of ['ring','middle','index']){
   for(const circumference of [49,50.6,52,55,56,59.55,65,67.2,69]){
    const r={finger,circumference,widthMm:circumference/Math.PI,quality:80};
    assert.deepEqual(resultWithAdjustedTable(r,percent),resultWithAdjustedTable(r,0));
   }
  }
 }
 assert.notEqual(resultWithAdjustedTable({finger:'little',circumference:55},4).size,resultWithAdjustedTable({finger:'little',circumference:55},0).size);
});
