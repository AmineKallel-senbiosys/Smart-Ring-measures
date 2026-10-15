export function lineWidthMm(line,review){
 const {imageWidth:w,imageHeight:h,pixelScale:scale}=review;
 if(![w,h,scale].every(v=>Number.isFinite(v)&&v>0)||!line||![line.a,line.b].every(p=>p&&[p.x,p.y].every(v=>Number.isFinite(v)&&v>=0&&v<=1)))throw new Error('Invalid photo measurement');
 return Math.hypot((line.b.x-line.a.x)*w,(line.b.y-line.a.y)*h)/scale;
}
export function reviewedResults(review){
 if(!review||review.fingers.length!==4||new Set(review.fingers.map(f=>f.finger)).size!==4)throw new Error('Four finger measurements required');
 return review.fingers.map(f=>{
  if(!f.confirmed||f.needsAdjustment)throw new Error('Confirm all four finger outlines first');
  const width=lineWidthMm(f.line,review);
  if(width<10||width>26)throw new Error('Finger width must be between 10 and 26 mm');
  const calibration=review.circumferenceModel;
  const model=calibration&&width>=calibration.minWidth&&width<=calibration.maxWidth?calibration:{slope:Math.PI,intercept:0};
  const circumference=width*model.slope+model.intercept;
  if(!Number.isFinite(circumference)||circumference<=0)throw new Error('Invalid circumference');
  return {finger:f.finger,widthMm:width,diameter:circumference/Math.PI,circumference,quality:f.quality,measurementSource:'photo-reviewed',sampleCount:f.sampleCount,calibrationId:model.id||null};
 });
}
