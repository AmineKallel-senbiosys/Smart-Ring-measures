"""Replay user-labeled scans; reference sizes are evaluation only."""
import json,sys
from pathlib import Path
import hand_worker as worker
import cv2

ROOT=Path(__file__).resolve().parent.parent/'test'
EXPECTED={'Test N1':[6,8,10,10],'Test N2':[8,10,10,10],'Test N3':[6,8,8,8]}
def run(output):
    evaluations=[]
    for name,expected in EXPECTED.items():
        captures=sorted((ROOT/name).glob('*-analyze-*/input.*'))
        if not captures:continue
        source=captures[-1];original=cv2.imread(str(source))
        for ratio in ([1] if '--original-only' in sys.argv else [1,.85,.7]):
            image=cv2.resize(original,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA) if ratio!=1 else original
            try:
                result=worker.analyze(image)
                values=[dict(finger=r['finger'],widthMm=r['widthMm'],circumference=r['circumference'],size=r['size'],quality=r['quality'],region=r.get('measurementRegion'),stability=r.get('stability')) for r in result['results']]
                row=dict(test=name,ratio=ratio,expected=expected,results=values,correct=sum(r['size']==e for r,e in zip(values,expected)),pixelScale=result['review']['pixelScale'])
            except Exception as e:row=dict(test=name,ratio=ratio,expected=expected,error=str(e),correct=0)
            evaluations.append(row);print(json.dumps(row),flush=True)
    Path(output).write_text(json.dumps(dict(referenceSource='User product sizes, not measured circumference; these scans are development data, not an independent validation set',evaluations=evaluations),indent=2),encoding='utf-8')
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else '../test/benchmark.json')
