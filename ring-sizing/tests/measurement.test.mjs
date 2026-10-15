import test from 'node:test';
import assert from 'node:assert/strict';
import {fromCircumference,fromPhoto} from '../dist/measurement.js';
test('US 7 ring converts from its inner circumference',()=>{const d=11.63+.8128*7;const r=fromCircumference(d*Math.PI);assert.equal(r.us,7);assert.ok(Math.abs(r.diameter-d)<1e-10);assert.equal(r.eu,54);});
test('photo calibration is invariant under image resizing',()=>{const a=fromPhoto(856,173.196,85.6);const b=fromPhoto(428,86.598,85.6);assert.equal(a.us,7);assert.equal(a.us,b.us);assert.ok(Math.abs(a.diameter-b.diameter)<1e-10);});
test('invalid, collapsed and out-of-range measurements are rejected',()=>{for(const value of [0,NaN,Infinity,39,81])assert.throws(()=>fromCircumference(value),RangeError);for(const input of [[0,20,85.6],[856,0,85.6],[856,170,0],[NaN,170,85.6],[100,100,85.6]])assert.throws(()=>fromPhoto(...input),RangeError);});
