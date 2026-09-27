"""
Unit tests for Object Detection module interface.
"""

import unittest
import numpy as np
from PIL import Image
from src.object_detection import ObjectDetector, get_object_detector


class TestObjectDetection(unittest.TestCase):

    def setUp(self):
        self.detector = get_object_detector()
        # Synthetic RGB image
        self.test_img = Image.new("RGB", (300, 300), color=(100, 150, 200))

    def test_detector_returns_tuple(self):
        dets, ann_img = self.detector.detect_objects(self.test_img)
        self.assertIsInstance(dets, list)
        self.assertIsInstance(ann_img, np.ndarray)

    def test_detection_structure(self):
        dets, ann_img = self.detector.detect_objects(self.test_img)
        if dets:
            d = dets[0]
            self.assertIn("object_name", d)
            self.assertIn("confidence", d)
            self.assertIn("bbox", d)
            self.assertEqual(len(d["bbox"]), 4)


if __name__ == "__main__":
    unittest.main()
