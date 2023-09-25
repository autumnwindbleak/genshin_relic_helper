import unittest

from cnocr import CnOcr


class CnOCRTestMethods(unittest.TestCase):

    def test_single_line(self):
        ocr = CnOcr(det_model_name='naive_det')
        img_fp = '../resources/img/cnocr_test_img.png'
        out = ocr.ocr_for_single_line(img_fp)
        self.assertEqual(out['text'], '如蜜的终宴')


if __name__ == '__main__':
    unittest.main()
