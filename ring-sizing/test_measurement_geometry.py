import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'.vision-tools'))
import cv2
import numpy as np
from measurement_geometry import CARD,card_calibration,finger_width,circumference_from_width
from fit_rules import fit_for_circumference

class MeasurementTests(unittest.TestCase):
    def test_card_scale_with_rotation_and_corner_noise(self):
        angle=.28;r=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
        q=CARD@r*4+np.array([200,100])+np.array([[.2,-.2],[-.2,.1],[.1,.2],[-.1,-.1]])
        self.assertAlmostEqual(card_calibration(q),4,delta=.01)

    def test_reject_low_resolution_and_perspective(self):
        with self.assertRaisesRegex(ValueError,'too small'):card_calibration(CARD*1.1)
        q=CARD*4;q[2,0]-=35
        with self.assertRaisesRegex(ValueError,'angled'):card_calibration(q)

    def test_width_on_known_pixel_silhouettes(self):
        # Known 18 and 20 mm silhouettes at 5 px/mm. Bright AND dark hands,
        # with a neighboring silhouette that must not count towards the width.
        for diameter in [18,20]:
            for skin,bg in [((130,170,215),(20,30,40)),((45,70,95),(210,220,230))]:
                image=np.full((500,500,3),bg,np.uint8)
                lo=int(250-diameter*5/2);hi=int(250+diameter*5/2)
                image[90:400,lo:hi]=skin
                image[90:400,hi+25:hi+80]=skin
                width,mad=finger_width(image,np.array([250.,370.]),np.array([250.,170.]),5)
                self.assertAlmostEqual(width,diameter,delta=.15)
                self.assertLess(mad,.05)
                self.assertEqual(fit_for_circumference(circumference_from_width(width))['size'],8 if diameter==18 else 10)

    def test_non_contrasting_photo_does_not_return_a_size(self):
        image=np.full((500,500,3),140,np.uint8)
        with self.assertRaisesRegex(ValueError,'could not'):finger_width(image,np.array([250.,370.]),np.array([250.,170.]),5)

    def test_clear_finger_with_offset_landmark_and_close_neighbor(self):
        image=np.full((500,500,3),30,np.uint8)
        image[90:400,205:295]=210  # 18 mm finger, centre at x=250
        image[90:400,310:400]=210  # separated by a clear 3 mm gap
        width,mad=finger_width(image,np.array([259.,370.]),np.array([259.,170.]),5,neighbors=[(np.array([355.,370.]),np.array([355.,170.]))])
        self.assertAlmostEqual(width,18,delta=.15)

    def test_blurred_finger_does_not_produce_a_confident_size(self):
        image=np.full((500,500,3),30,np.uint8);image[90:400,205:295]=210
        image=cv2.GaussianBlur(image,(0,0),8)
        with self.assertRaisesRegex(ValueError,'could not'):finger_width(image,np.array([250.,370.]),np.array([250.,170.]),5)

    def test_clear_moderate_contrast_outline(self):
        image=np.full((500,500,3),(130,160,190),np.uint8)
        image[90:400,205:295]=(150,180,210)
        width,_=finger_width(image,np.array([250.,370.]),np.array([250.,170.]),5)
        self.assertAlmostEqual(width,18,delta=.15)

    def test_clear_narrow_gap_and_asymmetric_landmark(self):
        image=np.full((500,500,3),30,np.uint8)
        image[90:400,205:295]=210
        image[90:400,300:390]=210
        width,_=finger_width(image,np.array([265.,370.]),np.array([265.,170.]),5,neighbors=[(np.array([345.,370.]),np.array([345.,170.]))])
        self.assertAlmostEqual(width,18,delta=.15)

    def test_clear_rotated_finger(self):
        image=np.full((500,500,3),30,np.uint8);image[90:400,205:295]=210
        matrix=cv2.getRotationMatrix2D((250,250),25,1)
        image=cv2.warpAffine(image,matrix,(500,500),borderValue=(30,30,30))
        mcp,pip=cv2.transform(np.array([[[250.,370.],[250.,170.]]]),matrix)[0]
        width,_=finger_width(image,mcp,pip,5)
        self.assertAlmostEqual(width,18,delta=.25)

    def test_same_formula_as_reference_camera_scan(self):
        # Reference: 85.6 / cardPx * fingerPx, followed by pi. No .85
        # ellipse reduction, clamped default diameter or rounded intermediate.
        for card_px,finger_px in [(428,90),(513.6,120),(342.4,76)]:
            scale=card_calibration(CARD*(card_px/85.6))
            self.assertAlmostEqual(circumference_from_width(finger_px/scale),finger_px*85.6/card_px*math.pi,places=10)

if __name__=='__main__':unittest.main()
