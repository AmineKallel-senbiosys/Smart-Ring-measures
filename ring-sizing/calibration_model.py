"""Fit circumference against observed width with held-person-out validation.

No public case-study coefficients or guessed depth ratios are used. Training
requires real pairs from this pipeline; no calibration ships enabled.
"""
import csv,hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'.vision-tools'))
import numpy as np

METHOD='neural-hand-segmentation-v3'

def fit_calibration(rows):
    if len(rows)<30:raise ValueError('At least 30 real measurement pairs are required.')
    if any(not r.get('person','').strip() or r.get('finger') not in ['little','ring','middle','index'] for r in rows):raise ValueError('Use a stable anonymous person code and a valid finger label in each row.')
    people={r['person'] for r in rows}
    if len(people)<5:raise ValueError('At least five different people are required for held-person-out validation.')
    x=np.array([float(r['width_mm']) for r in rows]);y=np.array([float(r['circumference_mm']) for r in rows])
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or np.any((x<10)|(x>26)) or np.any((y<30)|(y>100)):raise ValueError('Invalid physical measurements.')
    def fit(a,b):
        if np.ptp(a)<2:raise ValueError('The calibration widths must span at least 2 mm in every training fold.')
        coefficients=np.linalg.lstsq(np.column_stack([a,np.ones(len(a))]),b,rcond=None)[0]
        if not 1<coefficients[0]<5:raise ValueError('The fitted relationship is not physically plausible.')
        return coefficients
    predictions=np.zeros(len(rows))
    for person in people:
        test=np.array([r['person']==person for r in rows]);coefficients=fit(x[~test],y[~test]);predictions[test]=x[test]*coefficients[0]+coefficients[1]
    error=predictions-y;mae=float(np.mean(np.abs(error)));rmse=float(np.sqrt(np.mean(error**2)));maximum=float(np.max(np.abs(error)))
    if mae>.75 or maximum>2:raise ValueError(f'Calibration did not pass held-person-out validation: MAE {mae:.3f} mm, max error {maximum:.3f} mm. Collect better measurements; do not deploy this model.')
    slope,intercept=fit(x,y)
    fingerprint=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()[:12]
    return dict(version=1,id=f'validated-{fingerprint}',method=METHOD,slope=float(slope),intercept=float(intercept),minWidth=float(x.min()),maxWidth=float(x.max()),validation=dict(protocol='leave-one-person-out',people=len(people),pairs=len(rows),maeMm=mae,rmseMm=rmse,maxErrorMm=maximum))

def load_calibration(path):
    path=Path(path)
    if not path.exists():return None
    model=json.loads(path.read_text(encoding='utf-8'))
    v=model.get('validation',{})
    if model.get('method')!=METHOD or model.get('version')!=1 or v.get('protocol')!='leave-one-person-out' or v.get('people',0)<5 or v.get('pairs',0)<30 or not 0<=v.get('maeMm',math.inf)<=.75 or not 0<=v.get('maxErrorMm',math.inf)<=2:
        raise ValueError('The calibration file is incompatible or has not passed validation.')
    if not all(math.isfinite(model.get(k,float('nan'))) for k in ['slope','intercept','minWidth','maxWidth']) or not 1<model['slope']<5 or not 10<=model['minWidth']<model['maxWidth']<=26:raise ValueError('Invalid calibration coefficients.')
    return model

def calibrated_circumference(width,model):
    if model and model['minWidth']<=width<=model['maxWidth']:
        return width*model['slope']+model['intercept'],model['id']
    return width*math.pi,None

if __name__=='__main__':
    import argparse,sys
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('csv');parser.add_argument('--output',default='measurement-calibration.json');args=parser.parse_args()
    try:
        with open(args.csv,encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        model=fit_calibration(rows)
        Path(args.output).write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(model['validation'],indent=2))
    except (ValueError,KeyError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
