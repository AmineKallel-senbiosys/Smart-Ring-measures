import hand_worker as w
import cv2,numpy as np
image=cv2.imread('../record-review/hand-test.png');h,width=image.shape[:2]
detected=w.model.detect(w.mp.Image(image_format=w.mp.ImageFormat.SRGB,data=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)))
print('hand boxes',[(min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)) for pts in detected.hand_landmarks])
edges=np.zeros((h,width),np.uint8)
for channel in cv2.split(image):edges=cv2.bitwise_or(edges,cv2.Canny(channel,35,100))
edges=cv2.morphologyEx(edges,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
for c in contours:
 a=abs(cv2.contourArea(c))
 if not width*h*.002<a<width*h*.3:continue
 q=cv2.approxPolyDP(c,.03*cv2.arcLength(c,True),True)
 cv2.drawContours(image,[q],-1,(0,255,0),1)
 print('contour',len(q),round(a),cv2.boundingRect(c))
for points in detected.hand_landmarks:
 for p in points:cv2.circle(image,(int(p.x*width),int(p.y*h)),2,(0,0,255),-1)
cv2.imwrite('../record-review/debug-detection.png',image)
