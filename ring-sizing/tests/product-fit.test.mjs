import test from 'node:test';
import assert from 'node:assert/strict';
import {fitForCircumference,PRODUCT_FIT} from '../product-fit.mjs';
test('all table boundaries preserve exact inclusivity',()=>{
 const cases=[[50.599999,null,'out-of-range'],[50.6,6,'loose'],[51.249999,6,'loose'],[51.25,6,'ok'],[51.9,6,'ok'],[51.900001,6,'tight'],[54.449999,6,'tight'],[54.45,8,'loose'],[55.724999,8,'loose'],[55.725,8,'ok'],[57,8,'ok'],[57.000001,8,'tight'],[59.549999,8,'tight'],[59.55,10,'loose'],[60.824999,10,'loose'],[60.825,10,'ok'],[62.1,10,'ok'],[62.100001,10,'tight'],[64.649999,10,'tight'],[64.65,12,'loose'],[65.924999,12,'loose'],[65.925,12,'ok'],[67.2,12,'ok'],[67.200001,null,'out-of-range'],[80,null,'out-of-range']];
 for(const [c,size,zone] of cases)assert.deepEqual(fitForCircumference(c),{size,zone,outOfRange:size===null},'C='+c);
});
test('only the four product sizes can be selected across the complete interval',()=>{for(let c=50.6;c<=67.2;c+=.001)assert.ok([6,8,10,12].includes(fitForCircumference(c).size));assert.deepEqual(PRODUCT_FIT.map(r=>r.size),[6,8,10,12]);});
test('invalid circumferences are rejected',()=>{for(const c of [NaN,Infinity,-1,0])assert.throws(()=>fitForCircumference(c),RangeError);});
