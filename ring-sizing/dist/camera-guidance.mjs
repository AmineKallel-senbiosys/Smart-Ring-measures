export function coverCrop(width,height,displayWidth,displayHeight){
 if(![width,height,displayWidth,displayHeight].every(v=>Number.isFinite(v)&&v>0))throw new Error('Invalid camera dimensions');
 const target=displayWidth/displayHeight,source=width/height;
 const cropWidth=source>target?height*target:width,cropHeight=source>target?height:width/target;
 return {x:(width-cropWidth)/2,y:(height-cropHeight)/2,width:cropWidth,height:cropHeight};
}
export function phoneLevel(beta,gamma,screenAngle=0){
 if(![beta,gamma,screenAngle].every(Number.isFinite))return null;
 const b=beta*Math.PI/180,g=gamma*Math.PI/180,a=screenAngle*Math.PI/180;
 const z=Math.cos(b)*Math.cos(g),angle=Math.acos(Math.min(1,Math.abs(z)))*180/Math.PI;
 const gx=Math.sin(g),gy=Math.sin(b)*Math.cos(g);
 const x=gx*Math.cos(a)+gy*Math.sin(a),y=-gx*Math.sin(a)+gy*Math.cos(a);
 return {angle,x:Math.max(-1,Math.min(1,x)),y:Math.max(-1,Math.min(1,y))};
}
