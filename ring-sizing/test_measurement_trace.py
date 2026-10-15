import unittest,json,math
from test_hand_segmentation import hand_fixture
from hand_segmentation import measure_finger
from measurement_trace import calculation_trace,annotated_image
from fit_rules import fit_for_circumference
import cv2,numpy as np

class MeasurementTraceTests(unittest.TestCase):
    def test_trace_tracks_real_sample_widths_and_matches_size_formula(self):
        image,lm,card,mask=hand_fixture();trace={'finger':'index'}
        result=measure_finger(image,mask,lm[5],lm[6],4,[(lm[9],lm[10])],diagnostics=trace,distal=lm[7])
        width=result['widthMm'];mad=result['spreadMm'];circumference=width*math.pi;fit=fit_for_circumference(circumference)
        calculation=calculation_trace(width,mad,4,result,'mobilesam',circumference,None,None,fit,95)
        trace.update(calculation=calculation,selectedLinePx=dict(left=result['left'].tolist(),right=result['right'].tolist()))
        for section in trace['sections']:
            if 'widthPixels' in section:self.assertAlmostEqual(section['widthPixels']/4,section['widthMm'])
        self.assertEqual(sum(s['status']=='accepted' for s in trace['sections']),result['sampleCount'])
        self.assertAlmostEqual(calculation['circumference']['valueMm'],width*math.pi)
        self.assertEqual(calculation['product']['selectedSize'],fit['size'])
        json.dumps(trace,allow_nan=False)
        overlay=cv2.imdecode(np.frombuffer(annotated_image(image,card,[trace]),np.uint8),cv2.IMREAD_COLOR)
        self.assertEqual(overlay.shape,image.shape)
        self.assertFalse(np.array_equal(overlay,image))

    def test_calibrated_formula_and_quality_caps_are_explicit(self):
        measured={'contourFraction':.2,'nearJoint':True}
        result=calculation_trace(18,.1,4,measured,'grabcut',56.5,{'slope':3,'intercept':2.5},'validated-example',fit_for_circumference(56.5),55)
        self.assertEqual(result['circumference']['formula'],'widthMm * slope + intercept')
        self.assertEqual(result['circumference']['slope'],3)
        self.assertEqual([c['maximum'] for c in result['quality']['caps']],[55,70,65])
        self.assertEqual(result['product']['rule']['size'],8)

if __name__=='__main__':unittest.main()
