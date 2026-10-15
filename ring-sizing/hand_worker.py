import sys, json, base64, math, os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.vision-tools'))
import cv2
import numpy as np
import mediapipe as mp
from fit_rules import fit_for_circumference
from measurement_geometry import card_calibration, finger_width, circumference_from_width
from hand_segmentation import segment_hand, measure_finger
from calibration_model import load_calibration, calibrated_circumference
from neural_hand_mask import neural_mask
from hand_detection import detect_hands
from measurement_trace import calculation_trace,annotated_image
from measurement_stability import compare_measurements

options=mp.tasks.vision.HandLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(ROOT/'dist/vision/hand_landmarker.task')),num_hands=2,min_hand_detection_confidence=.35,min_hand_presence_confidence=.4)
model=mp.tasks.vision.HandLandmarker.create_from_options(options)

def detector(rgb):
    result=model.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb))
    return [np.array([(p.x,p.y) for p in hand],dtype=float) for hand in result.hand_landmarks]

def ordered(q):
    center=np.mean(q,axis=0)
    q=np.array(sorted(q,key=lambda p:math.atan2(p[1]-center[1],p[0]-center[0])),dtype=np.float32)
    q=np.roll(q,-int(np.argmin(q.sum(axis=1))),axis=0)
    if np.linalg.norm(q[0]-q[1])<np.linalg.norm(q[1]-q[2]):q=np.roll(q,-1,axis=0)
    return q

def card_quad(image,lm):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(cv2.GaussianBlur(gray,(5,5),0),25,80)
    for channel in cv2.split(image):edges=cv2.bitwise_or(edges,cv2.Canny(channel,35,100))
    edges=cv2.morphologyEx(edges,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    found,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    contours=list(found)
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    masks=[cv2.inRange(hsv,np.array([start,45,45]),np.array([min(179,start+30),255,255])) for start in range(0,180,15)]
    masks.append(cv2.inRange(hsv,np.array([0,0,170]),np.array([179,55,255])))
    for mask in masks:
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        extra,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours.extend(extra)
    candidates=[];h,w=image.shape[:2];hand_y=np.mean(lm[[5,9,13,17],1])
    for contour in contours:
        area=abs(cv2.contourArea(contour))
        if not w*h*.002<area<w*h*.3:continue
        quad=cv2.approxPolyDP(contour,.03*cv2.arcLength(contour,True),True)
        if len(quad)!=4 or not cv2.isContourConvex(quad):continue
        original=ordered(quad.reshape(4,2));original_sides=[np.linalg.norm(original[i]-original[(i+1)%4]) for i in range(4)]
        if max(abs(original_sides[0]-original_sides[2])/max(original_sides[0],original_sides[2]),abs(original_sides[1]-original_sides[3])/max(original_sides[1],original_sides[3]))>.08:continue
        # Fit the full outer contour: polygon corner simplification can shrink
        # a rounded card and systematically inflate all finger measurements.
        rectangle=cv2.minAreaRect(contour)
        if area/(rectangle[1][0]*rectangle[1][1]+1e-8)<.8:continue
        q=ordered(cv2.boxPoints(rectangle));sides=[np.linalg.norm(q[i]-q[(i+1)%4]) for i in range(4)]
        a=(sides[0]+sides[2])/2;b=(sides[1]+sides[3])/2
        if b<20 or not 1.25<a/b<2 or np.mean(q[:,1])>hand_y:continue
        perspective=max(sides[0],sides[2])/min(sides[0],sides[2])
        if perspective>1.5:continue
        candidates.append((abs(a/b-85.6/53.98)+abs(perspective-1)*.25-.00001*area,q))
    if not candidates:raise ValueError('The standard card was not detected. Keep all four card edges visible above your hand, on the same flat surface.')
    return min(candidates,key=lambda item:item[0])[1]

def analyze_once(image,inspect=False,on_stage=lambda stage:None,save_debug=True):
    h,w=image.shape[:2];factor=min(1,2400/max(w,h))
    if factor<1:image=cv2.resize(image,None,fx=factor,fy=factor);h,w=image.shape[:2]
    on_stage(0)
    hands=detect_hands(image,detector)
    if not hands:
        if inspect:return dict(hand=False,card=False,spread=False,flat=False)
        raise ValueError('No hand was detected. Show your whole hand, palm down, with all four fingers separated.')
    lm=max(hands,key=lambda points:np.ptp(points[:,0])*np.ptp(points[:,1]))
    try:q=card_quad(image,lm)
    except ValueError:
        if inspect:return dict(hand=True,card=False,spread=False,flat=False)
        raise
    length=np.linalg.norm(lm[9]-lm[10]);spread=all(np.linalg.norm(lm[a]-lm[b])>length*.6 for a,b in [(8,12),(12,16),(16,20)])
    visible_points=lm[[5,8,9,12,13,16,17,20]]/np.array([w,h])
    framed=bool(np.all((visible_points>.025)&(visible_points<.975)) and np.all((q/np.array([w,h])>.015)&(q/np.array([w,h])<.985)))
    try:
        card_calibration(q,False)
        flat=True
    except ValueError:flat=False
    if inspect:return dict(hand=True,card=True,spread=bool(spread),flat=bool(flat),framed=framed,pixelScale=float((np.linalg.norm(q[0]-q[1])+np.linalg.norm(q[2]-q[3]))/(2*85.6)))
    on_stage(1)
    if not spread:raise ValueError('Separate all four fingers so their edges do not touch, then retake the photo.')
    scale=card_calibration(q);results=[];fingers=[];traces=[];calibration=load_calibration(ROOT/'measurement-calibration.json')
    mask_source='mobilesam'
    try:mask=neural_mask(image,lm,q)
    except (ValueError,ImportError,RuntimeError):
        mask_source='grabcut'
        try:mask=segment_hand(image,lm,q)
        except (ValueError,cv2.error):mask=None
    def point(p):return dict(x=float(p[0]/w),y=float(p[1]/h))
    for name,mcp,pip,tip,adjacent in [('little',17,18,20,[13]),('ring',13,14,16,[9,17]),('middle',9,10,12,[5,13]),('index',5,6,8,[9])]:
        trace=dict(finger=name,landmarkIndices=dict(mcp=mcp,pip=pip,distal=pip+1,tip=tip),landmarksPx=dict(mcp=lm[mcp].tolist(),pip=lm[pip].tolist(),distal=lm[pip+1].tolist(),tip=lm[tip].tolist()),maskSource=mask_source)
        traces.append(trace)
        try:
            if mask is None:raise ValueError('The hand outline needs manual alignment.')
            measured=measure_finger(image,mask,lm[mcp],lm[pip],scale,[(lm[n],lm[n+1]) for n in adjacent],diagnostics=trace,distal=lm[pip+1])
        except ValueError as error:
            trace.update(measured=False,error=str(error),calculation=None)
            # Never convert a landmark-width prior into an automatic size.
            reason='inconsistent-widths' if 'disagree' in str(error) else 'hand-outline-unavailable' if mask is None else 'finger-edges-unavailable'
            results.append(dict(finger=name,measured=False,diameter=None,circumference=None,widthMm=None,quality=0,size=None,zone='unmeasured',outOfRange=False,measurementSource='unmeasured',failureReason=reason))
            axis=lm[pip]-lm[mcp];normal=np.array([-axis[1],axis[0]])/np.linalg.norm(axis)
            centre=lm[mcp]+axis*.55;half=normal*np.clip(np.linalg.norm(axis)*.3,5*scale,13*scale)
            fingers.append(dict(finger=name,needsAdjustment=True,message=str(error),line=dict(a=point(centre-half),b=point(centre+half)),lines=[],quality=0,sampleCount=0))
            continue
        median=measured['widthMm'];mad=measured['spreadMm']
        diameter=median
        quality=int(max(20,min(95,round(95-400*mad/median),round(scale*22+35))))
        if measured['contourFraction']>0:quality=min(quality,55)
        if measured['nearJoint']:quality=min(quality,70)
        if mask_source=='grabcut':quality=min(quality,65)
        circumference,calibration_id=calibrated_circumference(median,calibration)
        fit=fit_for_circumference(circumference)
        trace.update(measured=True,selectedLinePx=dict(left=measured['left'].tolist(),right=measured['right'].tolist()),sampleCount=measured['sampleCount'],calculation=calculation_trace(median,mad,scale,measured,mask_source,circumference,calibration,calibration_id,fit,quality))
        results.append(dict(finger=name,diameter=round(circumference/math.pi,2),circumference=circumference,widthMm=round(median,2),quality=quality,spreadMm=round(mad,2),measurementSource='photo',calibrationId=calibration_id,maskSource=mask_source,measurementRegion='near-joint' if measured['nearJoint'] else 'proximal',**fit))
        fingers.append(dict(finger=name,needsAdjustment=False,line=dict(a=point(measured['left']),b=point(measured['right'])),lines=[dict(a=point(s['left']),b=point(s['right'])) for s in measured['samples']],quality=quality,widthMm=median,sampleCount=measured['sampleCount'],method=measured['method']))
    on_stage(2)
    output=dict(results=results,review=dict(card=[point(p) for p in q],landmarks=[point(p) for p in lm],fingers=fingers,imageWidth=w,imageHeight=h,pixelScale=scale,maskSource=mask_source,method='neural-hand-segmentation-v3',circumferenceModel=calibration))
    if save_debug and os.environ.get('RING_TEST_CAPTURE')!='0':
        overlay=annotated_image(image,q,traces)
        output['debug']=dict(card=dict(widthMm=85.6,heightMm=53.98,cornersPx=q.tolist(),longEdgePixels=[float(np.linalg.norm(q[0]-q[1])),float(np.linalg.norm(q[2]-q[3]))],pixelsPerMm=scale,formula='mean(two card long edges in pixels) / 85.6'),fingers=traces)
        if overlay:output['annotatedImageBase64']=base64.b64encode(overlay).decode('ascii')
    return output

def analyze(image,inspect=False,on_stage=lambda stage:None):
    result=analyze_once(image,inspect,on_stage)
    if inspect:return result
    ratio=.85
    if result['review']['pixelScale']*ratio<3:
        for finger in result['results']:finger['stability']=dict(checked=False,reason='insufficient-resolution-for-second-scale')
        return result
    h,w=image.shape[:2];normalization=min(1,2400/max(w,h))
    comparison=cv2.resize(image,None,fx=normalization*ratio,fy=normalization*ratio,interpolation=cv2.INTER_AREA)
    try:
        second=analyze_once(comparison,save_debug=False)
        compare_measurements(result['results'],second['results'],ratio)
    except (ValueError,RuntimeError) as error:
        for finger in result['results']:
            if finger.get('measured') is not False:finger['quality']=min(finger['quality'],50)
            finger['stability']=dict(checked=True,stable=False,reason='comparison-failed',detail=str(error),candidateSizes=[])
    if 'debug' in result:
        for trace,finger in zip(result['debug']['fingers'],result['results']):
            trace['stability']=finger.get('stability')
            if trace.get('calculation'):
                quality=trace['calculation']['quality']
                if finger.get('stability',{}).get('stable') is False:quality['caps'].append(dict(reason='second-scale disagreement',maximum=50))
                quality['finalPercent']=finger['quality']
        overlay_source=cv2.resize(image,(result['review']['imageWidth'],result['review']['imageHeight']))
        overlay=annotated_image(overlay_source,np.array(result['debug']['card']['cornersPx']),result['debug']['fingers'])
        if overlay:result['annotatedImageBase64']=base64.b64encode(overlay).decode('ascii')
    return result

print(json.dumps({'ready':True}),flush=True)
for line in sys.stdin:
    try:
        job=json.loads(line);data=np.frombuffer(base64.b64decode(job['image']),np.uint8);image=cv2.imdecode(data,cv2.IMREAD_COLOR)
        if image is None:raise ValueError('The photo could not be read.')
        result=analyze(image,job.get('mode')=='inspect',lambda stage:print(json.dumps({'id':job['id'],'stage':stage}),flush=True))
        print(json.dumps({'id':job['id'],'result':result}),flush=True)
    except Exception as e:print(json.dumps({'id':job.get('id'),'error':str(e)}),flush=True)
    finally:
        if isinstance(job,dict):job.pop('image',None)
        image=None;data=None;result=None
