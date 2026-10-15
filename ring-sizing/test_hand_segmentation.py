import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'.vision-tools'))
import cv2
import numpy as np
from hand_segmentation import segment_hand,measure_finger,refine_edge

def hand_fixture():
    rng=np.random.default_rng(7)
    image=np.clip(rng.normal([70,95,120],3,(900,900,3)),0,255).astype(np.uint8)
    lm=np.array([[450,800],[630,675],[690,610],[750,555],[805,530],[580,520],[580,370],[580,265],[580,185],[470,525],[470,355],[470,235],[470,125],[360,535],[360,380],[360,275],[360,195],[260,550],[230,445],[210,370],[200,305]],float)
    skin=(145,180,215);truth=np.zeros((900,900),np.uint8)
    cv2.fillConvexPoly(truth,np.array([[250,535],[605,500],[660,660],[530,825],[380,825]],np.int32),1)
    for chain,width in [([1,2,3,4],80),([5,6,7,8],80),([9,10,11,12],80),([13,14,15,16],72),([17,18,19,20],64)]:
        cv2.polylines(truth,[lm[chain].astype(np.int32)],False,1,width)
    image[truth==1]=skin
    card=np.array([[20,20],[362.4,20],[362.4,235.92],[20,235.92]],np.float32)
    cv2.fillConvexPoly(image,card.astype(np.int32),(210,100,40))
    return image,lm,card,truth

class SegmentationTests(unittest.TestCase):
    def test_landmark_guided_mask_and_ring_zone_measurement(self):
        image,lm,card,truth=hand_fixture();mask=segment_hand(image,lm,card)
        self.assertEqual(int(mask[100,100]),0)
        for mcp,pip,width,neighbors in [(5,6,20,[9]),(9,10,20,[5,13]),(13,14,18,[9,17]),(17,18,16,[13])]:
            result=measure_finger(image,mask,lm[mcp],lm[pip],4,[(lm[n],lm[n+1]) for n in neighbors])
            self.assertAlmostEqual(result['widthMm'],width,delta=.4)
            self.assertGreaterEqual(result['sampleCount'],8)
            self.assertEqual(result['method'],'segmentation-subpixel')

    def test_subpixel_edges_with_antialiasing_and_both_contrast_directions(self):
        for fg,bg in [(210,30),(30,210)]:
            image=np.full((350,350,3),bg,np.uint8);image[:,130:220]=fg
            image=cv2.GaussianBlur(image,(0,0),1)
            left=refine_edge(image,np.array([130.,180.]),np.array([1.,0.]),5)
            right=refine_edge(image,np.array([220.,180.]),np.array([1.,0.]),5)
            self.assertAlmostEqual(float(np.linalg.norm(right-left)),90,delta=.25)

    def test_absent_image_edges_cannot_be_accepted_as_measurements(self):
        image=np.full((350,350,3),150,np.uint8);mask=np.zeros((350,350),np.uint8);mask[:,130:220]=1
        with self.assertRaisesRegex(ValueError,'manual alignment'):
            measure_finger(image,mask,np.array([175.,300.]),np.array([175.,100.]),5)

    def test_skin_outside_initial_skeleton_tube_is_not_locked_as_background(self):
        image,lm,card,truth=hand_fixture()
        # A short, shifted phalanx estimate makes its initial tube narrower
        # than the true skin. It must remain recoverable by segmentation.
        lm[6]=[593,455]
        mask=segment_hand(image,lm,card)
        self.assertEqual(int(truth[450,547]),1)
        self.assertEqual(int(mask[450,547]),1)

if __name__=='__main__':unittest.main()
