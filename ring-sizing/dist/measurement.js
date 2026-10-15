// Standalone estimates. This is not a Circular-specific size chart.
export const US_SIZES = Array.from({length:25},(_,i)=>3+i/2);
export function fromCircumference(circumference){
  if(!Number.isFinite(circumference)||circumference<40||circumference>80) throw new RangeError('Circumference must be between 40 and 80 mm.');
  const diameter=circumference/Math.PI;
  const raw=(diameter-11.63)/.8128;
  const us=Math.round(raw*2)/2;
  return {us,diameter,circumference,eu:Math.round(circumference),between:Math.abs(raw-us)>.15};
}
export function fromPhoto(referencePixels,ringPixels,referenceMm){
  if(![referencePixels,ringPixels,referenceMm].every(x=>Number.isFinite(x)&&x>0))throw new RangeError('Choose two distinct points for each measurement.');
  return fromCircumference((ringPixels/referencePixels)*referenceMm*Math.PI);
}
