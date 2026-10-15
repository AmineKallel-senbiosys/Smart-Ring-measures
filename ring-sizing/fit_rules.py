import json,math
from pathlib import Path
RULES=json.loads((Path(__file__).resolve().parent/'product-fit.json').read_text())
def fit_for_circumference(c):
    if not math.isfinite(c) or c<=0:raise ValueError('Circumference must be positive, in mm.')
    for row in RULES:
        if c>=row['minimum'] and (row['maximumExclusive'] is None or c<row['maximumExclusive']) and c<=row.get('maximumInclusive',math.inf):
            zone='loose' if c<row['okMinimum'] else 'ok' if c<=row['okMaximum'] else 'tight'
            return dict(size=row['size'],zone=zone,outOfRange=False)
    return dict(size=None,zone='out-of-range',outOfRange=True)
