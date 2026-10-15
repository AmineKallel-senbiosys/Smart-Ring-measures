"""Expose processing sensitivity without treating it as circumference accuracy."""
def compare_measurements(primary,secondary,ratio):
    for result,other in zip(primary,secondary):
        if result.get('measured') is False:continue
        valid=other.get('measured') is not False and other.get('circumference') is not None
        delta=abs(result['circumference']-other['circumference']) if valid else None
        agrees=valid and result['size']==other['size'] and delta<=.75
        candidates=sorted({r['size'] for r in [result,other] if r.get('size') is not None})
        result['stability']=dict(checked=True,stable=bool(agrees),comparisonScale=ratio,circumferenceDifferenceMm=delta,comparisonCircumferenceMm=other.get('circumference'),candidateSizes=candidates,meaning='Sensitivity to image processing; not a validated physical error interval')
        if not agrees:result['quality']=min(result['quality'],50)
    return primary
