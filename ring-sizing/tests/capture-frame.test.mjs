import test from 'node:test';
import assert from 'node:assert/strict';
import {frameHasPixels,freezeFrame} from '../dist/capture-frame.mjs';
test('opaque black camera frames are rejected',()=>{
 const rgba=new Uint8ClampedArray(4000);for(let i=3;i<rgba.length;i+=4)rgba[i]=255;
 assert.equal(frameHasPixels(rgba),false);
 assert.equal(frameHasPixels(new Uint8ClampedArray()),false);
});
test('visible dark and normal frames retain pixels',()=>{
 const rgba=new Uint8ClampedArray(4000).fill(25);
 assert.equal(frameHasPixels(rgba),true);
});
test('snapshot copies pixels back and retains canvas without creating ImageBitmap',()=>{
 const pixels={data:new Uint8ClampedArray(16).fill(100)};let copied;
 const canvas={width:2,height:2,getContext:()=>({getImageData:()=>pixels,putImageData:value=>copied=value})};
 assert.equal(freezeFrame(canvas),canvas);assert.equal(copied,pixels);
});
