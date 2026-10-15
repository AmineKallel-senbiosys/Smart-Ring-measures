"""Check detector availability on private video frames, not physical accuracy."""
import hand_worker as worker
import cv2,numpy as np
from hand_segmentation import segment_hand,measure_finger
from neural_hand_mask import neural_mask
from measurement_geometry import card_calibration
for name,path in [('record1','../record-review/hand-test.png'),('record2','../record-review/record-2-frame-7.png')]:
    image=cv2.imread(path)
    if name=='record2':image=image[90:-100]
    h,w=image.shape[:2]
    d=worker.model.detect(worker.mp.Image(image_format=worker.mp.ImageFormat.SRGB,data=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)))
    if not d.hand_landmarks:print(name,'No hand detected');continue
    lm=max([np.array([(p.x*w,p.y*h) for p in ps]) for ps in d.hand_landmarks],key=lambda p:np.ptp(p[:,0])*np.ptp(p[:,1]))
    q=worker.card_quad(image,lm);scale=card_calibration(q,False);mask=neural_mask(image,lm,q)
    view=image.copy();view[mask==0]=(view[mask==0]*.25).astype(np.uint8)
    for i,p in enumerate(lm):cv2.putText(view,str(i),tuple(p.astype(int)),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,255,255),1)
    cv2.imwrite('../record-review/'+name+'-neural-hand.png',view[int(min(lm[[8,12,16,20],1]))-10:])
    print(name,'diagnostic only; resolution',round(scale,2),'px/mm')
    for finger,mcp,pip,adjacent in [('little',17,18,[13]),('ring',13,14,[9,17]),('middle',9,10,[5,13]),('index',5,6,[9])]:
        try:
            diagnostics={};result=measure_finger(image,mask,lm[mcp],lm[pip],scale,[(lm[n],lm[n+1]) for n in adjacent],diagnostics=diagnostics,distal=lm[pip+1])
            print(finger,'edges detected',result['sampleCount'])
        except ValueError:print(finger,'edges unavailable',diagnostics)
