export const BASE_FIT=Object.freeze([
 {size:6,min:50.6,okMin:51.25,okMax:51.9,maxEx:54.45},
 {size:8,min:54.45,okMin:55.725,okMax:57,maxEx:59.55},
 {size:10,min:59.55,okMin:60.825,okMax:62.1,maxEx:64.65},
 {size:12,min:64.65,okMin:65.925,okMax:67.2,maxEx:null,maxInclusive:67.2}
].map(Object.freeze));
export function adjustedFitTable(percent=0){
 if(!Number.isFinite(percent)||percent<=-100)throw new RangeError('Invalid table adjustment');
 const factor=1+percent/100;
 return BASE_FIT.map(r=>({...r,min:r.min*factor,okMin:r.okMin*factor,okMax:r.okMax*factor,maxEx:r.maxEx===null?null:r.maxEx*factor,maxInclusive:r.maxInclusive===undefined?undefined:r.maxInclusive*factor}));
}
export function fingerTablePercent(finger,percent=0){return finger==='little'?percent:0;}
export function resultWithAdjustedTable(result,percent=0){
 if(result.measured===false||!Number.isFinite(result.circumference))return result;
 const c=result.circumference,row=adjustedFitTable(fingerTablePercent(result.finger,percent)).find(r=>c>=r.min&&(r.maxEx===null||c<r.maxEx)&&(r.maxInclusive===undefined||c<=r.maxInclusive));
 if(!row)return {...result,size:null,zone:'out-of-range',outOfRange:true};
 return {...result,size:row.size,zone:c<row.okMin?'loose':c<=row.okMax?'ok':'tight',outOfRange:false};
}
