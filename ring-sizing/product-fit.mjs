import {readFileSync} from 'node:fs';
export const PRODUCT_FIT=JSON.parse(readFileSync(new URL('./product-fit.json',import.meta.url),'utf8'));
export function fitForCircumference(c){
 if(!Number.isFinite(c)||c<=0)throw new RangeError('Circumference must be a positive number in mm.');
 const row=PRODUCT_FIT.find(r=>c>=r.minimum&&(r.maximumExclusive===null||c<r.maximumExclusive)&&(r.maximumInclusive===undefined||c<=r.maximumInclusive));
 if(!row)return {size:null,zone:'out-of-range',outOfRange:true};
 return {size:row.size,zone:c<row.okMinimum?'loose':c<=row.okMaximum?'ok':'tight',outOfRange:false};
}
