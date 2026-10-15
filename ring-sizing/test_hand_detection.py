import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'.vision-tools'))
import numpy as np
from hand_detection import detect_hands,restore_points

class HandDetectionTests(unittest.TestCase):
    def test_rotations_preserve_original_measurement_coordinates(self):
        original=np.array([[.2,.3],[.7,.8]])
        variants=[original,np.column_stack((original[:,1],1-original[:,0])),1-original,np.column_stack((1-original[:,1],original[:,0]))]
        for turns,points in enumerate(variants):
            np.testing.assert_allclose(restore_points(points,turns,2000,1500),original*[2000,1500])

    def test_high_resolution_miss_retries_smaller_and_keeps_pixel_scale(self):
        calls=[]
        def detector(rgb):
            calls.append(rgb.shape)
            return [] if len(calls)==1 else [np.array([[.25,.5]])]
        result=detect_hands(np.zeros((1600,2400,3),np.uint8),detector)
        self.assertEqual(calls,[(1600,2400,3),(640,960,3)])
        np.testing.assert_allclose(result[0],[[600,800]])

    def test_blank_image_never_creates_hand(self):
        self.assertEqual(detect_hands(np.zeros((200,300,3),np.uint8),lambda rgb:[]),[])

if __name__=='__main__':unittest.main()
