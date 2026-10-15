import unittest,math
from fit_rules import fit_for_circumference,RULES
class FitRulesTests(unittest.TestCase):
    def test_exact_edges(self):
        for r in RULES:
            self.assertEqual(fit_for_circumference(r['minimum'])['size'],r['size'])
            self.assertEqual(fit_for_circumference(r['minimum'])['zone'],'loose')
            self.assertEqual(fit_for_circumference(math.nextafter(r['okMinimum'],-math.inf))['zone'],'loose')
            self.assertEqual(fit_for_circumference(r['okMinimum'])['zone'],'ok')
            self.assertEqual(fit_for_circumference(r['okMaximum'])['zone'],'ok')
            self.assertEqual(fit_for_circumference(math.nextafter(r['okMaximum'],math.inf))['zone'],'out-of-range' if r.get('maximumInclusive') is not None else 'tight')
            if r['maximumExclusive']:
                self.assertEqual(fit_for_circumference(math.nextafter(r['maximumExclusive'],-math.inf))['size'],r['size'])
                self.assertEqual(fit_for_circumference(r['maximumExclusive'])['size'],r['size']+2)
    def test_outside(self):
        self.assertIsNone(fit_for_circumference(50.599999)['size'])
        self.assertIsNone(fit_for_circumference(90)['size'])
if __name__=='__main__':unittest.main()
