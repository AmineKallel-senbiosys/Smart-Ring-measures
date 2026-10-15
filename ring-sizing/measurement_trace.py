"""Private debug overlay and exact numerical sizing steps."""
import math,cv2
from fit_rules import RULES

def calculation_trace(width,mad,scale,measured,mask_source,circumference,calibration,calibration_id,fit,quality):
    base=int(max(20,min(95,round(95-400*mad/width),round(scale*22+35))))
    caps=[]
    if measured['contourFraction']>0:caps.append(dict(reason='contour-only edges',maximum=55))
    if measured['nearJoint']:caps.append(dict(reason='near joint',maximum=70))
    if mask_source=='grabcut':caps.append(dict(reason='GrabCut fallback',maximum=65))
    row=next((r for r in RULES if r['size']==fit['size']),None)
    calibrated=calibration_id is not None
    return dict(widthMm=width,widthFormula='median(accepted edge distances in pixels / pixelsPerMm)',pixelsPerMm=scale,madMm=mad,
        circumference=dict(formula='widthMm * slope + intercept' if calibrated else 'widthMm * pi',pi=math.pi,slope=calibration['slope'] if calibrated else None,intercept=calibration['intercept'] if calibrated else None,calibrationId=calibration_id,valueMm=circumference,assumption=None if calibrated else 'Circular cross section; finger depth is not measured'),
        quality=dict(formula='max(20, min(95, round(95 - 400*MAD/width), round(scale*22 + 35)))',basePercent=base,caps=caps,finalPercent=quality,meaning='Image measurement quality, not probability of fit'),
        product=dict(inputCircumferenceMm=circumference,rule=row,allRules=RULES,selectedSize=fit['size'],zone=fit['zone'],formula='minimum <= C < maximumExclusive and C <= maximumInclusive when specified; loose if C < okMinimum; OK if C <= okMaximum; otherwise tight',usesUnroundedCircumference=True))

def annotated_image(image,quad,traces):
    view=image.copy()
    def xy(p):return tuple(int(round(v)) for v in p)
    for a,b in zip(quad,list(quad[1:])+[quad[0]]):cv2.line(view,xy(a),xy(b),(60,210,50),3)
    for index,trace in enumerate(traces):
        for section in trace.get('sections',[]):
            if 'leftPx' not in section:continue
            color=(220,170,30) if section['status']=='accepted' else (70,70,225)
            cv2.line(view,xy(section['leftPx']),xy(section['rightPx']),color,1)
        line=trace.get('selectedLinePx')
        if line:cv2.line(view,xy(line['left']),xy(line['right']),(170,35,240),4)
        value=trace.get('calculation',{})
        text=f"{trace['finger']}: "
        if value:text+=f"width {value['widthMm']:.2f}mm C {value['circumference']['valueMm']:.2f}mm US {value['product']['selectedSize']} {value['product']['zone']} Q{value['quality']['finalPercent']}%"
        else:text+='UNMEASURED: '+trace.get('error','')
        cv2.putText(view,text,(15,30+index*30),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)
    ok,encoded=cv2.imencode('.jpg',view,[cv2.IMWRITE_JPEG_QUALITY,94])
    return encoded.tobytes() if ok else None
