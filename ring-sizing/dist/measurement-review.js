import {lineWidthMm,reviewedResults} from './review-math.mjs';

export function mountMeasurementReview({app,photo,review,t,onConfirm,onRetake}){
 let selected=0,drag=null;
 review=structuredClone(review);
 review.fingers.forEach(f=>{f.confirmed=false;f.adjustedA=false;f.adjustedB=false;});
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 app.innerHTML=`<section class="measurement-review"><h1>${esc(t('reviewTitle'))}</h1><p>${esc(t('reviewHelp'))}</p><div class="review-photo"><canvas></canvas><svg role="group" aria-label="${esc(t('photoLines'))}" viewBox="0 0 ${review.imageWidth} ${review.imageHeight}"></svg></div><div class="review-finger-nav"><button id="review-prev" aria-label="${esc(t('previous'))}">‹</button><strong id="review-finger-name"></strong><button id="review-next" aria-label="${esc(t('next'))}">›</button></div><p class="review-reading" id="review-reading"></p><p class="review-hint" id="review-hint"></p><button class="scan-button" id="check-finger"></button><div class="review-progress" aria-label="${esc(t('reviewProgress'))}">${review.fingers.map((f,i)=>`<button data-finger="${i}" aria-label="${esc(t(f.finger))}">${i+1}</button>`).join('')}</div><p class="review-error" id="review-error" role="alert"></p><button class="scan-button" id="finish-review" disabled>${esc(t('useMeasurements'))}</button><button class="scan-link" id="review-retake">${esc(t('retakePhoto'))}</button><p class="review-note">${esc(t('reviewNote'))}</p></section>`;
 const canvas=app.querySelector('canvas'),svg=app.querySelector('svg');
 canvas.width=Math.min(1200,review.imageWidth);canvas.height=Math.round(canvas.width*review.imageHeight/review.imageWidth);
 canvas.getContext('2d').drawImage(photo,0,0,canvas.width,canvas.height);
 const xy=p=>`${p.x*review.imageWidth},${p.y*review.imageHeight}`;
 function paint(){
  const f=review.fingers[selected],radius=review.imageWidth*.018;
  svg.innerHTML=`<polygon points="${review.card.map(xy).join(' ')}" class="review-card"/>${review.fingers.map((g,i)=>`<line x1="${g.line.a.x*review.imageWidth}" y1="${g.line.a.y*review.imageHeight}" x2="${g.line.b.x*review.imageWidth}" y2="${g.line.b.y*review.imageHeight}" class="${i===selected?'review-line':'review-other-line'}"/>`).join('')}${(f.lines||[]).map(l=>`<line x1="${l.a.x*review.imageWidth}" y1="${l.a.y*review.imageHeight}" x2="${l.b.x*review.imageWidth}" y2="${l.b.y*review.imageHeight}" class="review-sample"/>`).join('')}${['a','b'].map(end=>`<circle cx="${f.line[end].x*review.imageWidth}" cy="${f.line[end].y*review.imageHeight}" r="${radius}" class="review-handle" tabindex="0" role="button" data-endpoint="${end}" aria-label="${esc(t(end==='a'?'firstEdge':'secondEdge'))}"/>`).join('')}`;
  app.querySelector('#review-finger-name').textContent=t(f.finger);
  const width=lineWidthMm(f.line,review);
  app.querySelector('#review-reading').textContent=f.needsAdjustment?t('alignmentRequired'):`${t('visibleWidth')}: ${width.toFixed(1)} mm`;
  app.querySelector('#review-hint').textContent=f.needsAdjustment?t('dragBoth'):t('checkEdges');
  const confirm=app.querySelector('#check-finger');confirm.textContent=t(f.confirmed?'fingerChecked':'confirmFinger');confirm.disabled=f.needsAdjustment||width<10||width>26;
  app.querySelectorAll('[data-finger]').forEach(b=>{const i=Number(b.dataset.finger);b.classList.toggle('checked',review.fingers[i].confirmed);b.classList.toggle('selected',i===selected);});
  app.querySelector('#finish-review').disabled=!review.fingers.every(g=>g.confirmed&&!g.needsAdjustment);
 }
 function adjust(end,x,y){
  const f=review.fingers[selected];f.line[end]={x:Math.max(0,Math.min(1,x)),y:Math.max(0,Math.min(1,y))};
  f[end==='a'?'adjustedA':'adjustedB']=true;f.confirmed=false;f.lines=[];
  if(f.adjustedA&&f.adjustedB)f.needsAdjustment=false;
  paint();
 }
 svg.addEventListener('pointerdown',e=>{
  const box=svg.getBoundingClientRect(),f=review.fingers[selected];
  const distances=['a','b'].map(end=>({end,d:Math.hypot(e.clientX-(box.x+f.line[end].x*box.width),e.clientY-(box.y+f.line[end].y*box.height))})).sort((a,b)=>a.d-b.d);
  if(distances[0].d>36)return;drag={end:distances[0].end,pointer:e.pointerId};svg.setPointerCapture(e.pointerId);e.preventDefault();
 });
 svg.addEventListener('pointermove',e=>{if(!drag||drag.pointer!==e.pointerId)return;const box=svg.getBoundingClientRect();adjust(drag.end,(e.clientX-box.x)/box.width,(e.clientY-box.y)/box.height);});
 const release=()=>{drag=null;};svg.addEventListener('pointerup',release);svg.addEventListener('pointercancel',release);
 svg.addEventListener('keydown',e=>{
  const end=e.target.dataset.endpoint;if(!end||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;
  e.preventDefault();const p=review.fingers[selected].line[end],step=.25*review.pixelScale;
  adjust(end,p.x+(e.key==='ArrowRight'?step:e.key==='ArrowLeft'?-step:0)/review.imageWidth,p.y+(e.key==='ArrowDown'?step:e.key==='ArrowUp'?-step:0)/review.imageHeight);
  svg.querySelector(`[data-endpoint="${end}"]`).focus();
 });
 for(const [id,delta] of [['review-prev',-1],['review-next',1]])app.querySelector('#'+id).onclick=()=>{selected=(selected+delta+4)%4;paint();};
 app.querySelectorAll('[data-finger]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.finger);paint();});
 app.querySelector('#check-finger').onclick=()=>{review.fingers[selected].confirmed=true;const unchecked=review.fingers.findIndex(f=>!f.confirmed);if(unchecked>=0)selected=unchecked;paint();};
 app.querySelector('#finish-review').onclick=async()=>{try{const measurements=reviewedResults(review);app.querySelector('#finish-review').disabled=true;await onConfirm(measurements);}catch(e){app.querySelector('#review-error').textContent=e.message;app.querySelector('#finish-review').disabled=false;}};
 app.querySelector('#review-retake').onclick=onRetake;
 paint();
}
