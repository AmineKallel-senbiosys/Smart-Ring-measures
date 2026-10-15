import unittest
import numpy as np
from calibration_model import fit_calibration,calibrated_circumference

class CalibrationTests(unittest.TestCase):
    def pairs(self):
        return [dict(person=f'p{person}',finger='ring',width_mm=16+i,circumference_mm=2.8*(16+i)+4+person*.03) for person in range(5) for i in range(6)]
    def test_systematic_bias_is_fitted_with_person_held_out(self):
        model=fit_calibration(self.pairs())
        self.assertAlmostEqual(model['slope'],2.8,places=10)
        self.assertLess(model['validation']['maeMm'],.1)
        c,identity=calibrated_circumference(18,model)
        self.assertAlmostEqual(c,54.46,places=2);self.assertEqual(identity,model['id'])
        c,identity=calibrated_circumference(25,model)
        self.assertAlmostEqual(c,25*np.pi);self.assertIsNone(identity)
    def test_one_person_or_unknown_circumferences_cannot_be_a_calibration(self):
        rows=self.pairs()
        for row in rows:row['person']='same-person'
        with self.assertRaisesRegex(ValueError,'five different'):fit_calibration(rows)
        with self.assertRaisesRegex(ValueError,'30 real'):fit_calibration([])
    def test_person_specific_overfit_is_not_activated(self):
        rows=self.pairs()
        for row in rows:row['circumference_mm']+=int(row['person'][1:])*2
        with self.assertRaisesRegex(ValueError,'did not pass'):fit_calibration(rows)
if __name__=='__main__':unittest.main()
