import test from 'node:test';
import assert from 'node:assert/strict';
import {SIZE_CHART,CARD_HEIGHT_MM,pixelsPerMm,ringPixels} from '../dist/screen-sizing.js';
test('screen calibration preserves physical ring diameter',()=>{for(const cardPixels of [180,260,330]){const scale=pixelsPerMm(cardPixels);assert.ok(Math.abs(scale*CARD_HEIGHT_MM-cardPixels)<1e-10);assert.ok(Math.abs(ringPixels(9,scale)/scale-18.9)<1e-10);}});
test('reference chart includes exact endpoints and product sizes',()=>{assert.equal(SIZE_CHART.length,9);assert.deepEqual(SIZE_CHART[0],{size:6,diameter:16.5});assert.deepEqual(SIZE_CHART.at(-1),{size:14,diameter:22.8});assert.ok(Math.abs(ringPixels(11,1)-20.5)<1e-10);});
test('unusable calibration and unknown product sizes are rejected',()=>{for(const value of [0,NaN,79,601])assert.throws(()=>pixelsPerMm(value),RangeError);assert.throws(()=>ringPixels(5,4),RangeError);assert.throws(()=>ringPixels(9,0),RangeError);});
