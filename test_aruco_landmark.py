import unittest

import cv2
import numpy as np

from landmark.aruco import ArUcoLandmarkDetector


class ArUcoLandmarkDetectorTest(unittest.TestCase):

    def test_detects_generated_marker(self):
        marker_id = 7
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        marker = cv2.aruco.generateImageMarker(dictionary, marker_id, 160)
        frame = np.full((240, 240, 3), 255, dtype=np.uint8)
        frame[40:200, 40:200] = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)

        detector = ArUcoLandmarkDetector("DICT_4X4_50")
        landmarks = detector.detect(frame)

        self.assertEqual(len(landmarks), 1)
        self.assertEqual(landmarks[0].marker_id, marker_id)
        self.assertEqual(landmarks[0].center, (119, 119))


if __name__ == "__main__":
    unittest.main()
