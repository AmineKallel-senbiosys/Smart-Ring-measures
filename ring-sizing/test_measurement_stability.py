import unittest
from measurement_stability import compare_measurements
class StabilityTests(unittest.TestCase):
    def test_disagreement_preserves_full_resolution_estimate_and_caps_quality(self):
        a=[dict(size=10,circumference=63.8,quality=95)]
        b=[dict(size=12,circumference=65.15,quality=94)]
        result=compare_measurements(a,b,.85)[0]
        self.assertEqual(result['size'],10)
        self.assertEqual(result['circumference'],63.8)
        self.assertEqual(result['quality'],50)
        self.assertEqual(result['stability']['candidateSizes'],[10,12])
        self.assertFalse(result['stability']['stable'])
    def test_same_size_with_large_metric_disagreement_is_unstable(self):
        result=compare_measurements([dict(size=8,circumference=56.,quality=90)],[dict(size=8,circumference=57.,quality=90)],.85)[0]
        self.assertFalse(result['stability']['stable'])
    def test_close_values_keep_quality(self):
        result=compare_measurements([dict(size=8,circumference=56.,quality=90)],[dict(size=8,circumference=56.1,quality=90)],.85)[0]
        self.assertTrue(result['stability']['stable']);self.assertEqual(result['quality'],90)
if __name__=='__main__':unittest.main()
