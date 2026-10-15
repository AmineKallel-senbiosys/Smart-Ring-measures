import unittest
from test_hand_segmentation import hand_fixture
from neural_hand_mask import neural_mask
from hand_segmentation import measure_finger

class NeuralMaskTests(unittest.TestCase):
    def test_local_model_separates_synthetic_hand_and_card(self):
        image,lm,card,_=hand_fixture();mask=neural_mask(image,lm,card)
        self.assertEqual(int(mask[100,100]),0)
        self.assertEqual(int(mask[420,580]),1)
        result=measure_finger(image,mask,lm[5],lm[6],4,[(lm[9],lm[10])],distal=lm[7])
        self.assertAlmostEqual(result['widthMm'],20,delta=.5)
        self.assertGreaterEqual(result['sampleCount'],8)
if __name__=='__main__':unittest.main()
