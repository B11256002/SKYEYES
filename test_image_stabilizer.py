import unittest

import cv2
import numpy as np

from stabilization.image import ImageStabilizer


class ImageStabilizerTest(unittest.TestCase):

    def test_disabled_stabilizer_returns_same_frame(self):
        frame = self._feature_frame()
        stabilizer = ImageStabilizer(enabled=False)

        result = stabilizer.stabilize(frame)

        self.assertIs(result, frame)

    def test_first_frame_sets_reference(self):
        frame = self._feature_frame()
        stabilizer = ImageStabilizer()

        result = stabilizer.stabilize(frame)

        self.assertIs(result, frame)
        self.assertIsNotNone(stabilizer.reference_gray)
        self.assertIsNotNone(stabilizer.reference_keypoints)

    def test_stabilized_frame_keeps_original_shape(self):
        frame = self._feature_frame()
        shifted = self._shift_frame(frame, dx=8, dy=6)
        stabilizer = ImageStabilizer(max_features=800, min_matches=8)

        stabilizer.stabilize(frame)
        result = stabilizer.stabilize(shifted)

        self.assertEqual(result.shape, shifted.shape)

    def _feature_frame(self):
        frame = np.full((240, 320, 3), 255, dtype=np.uint8)

        cv2.rectangle(frame, (40, 40), (120, 120), (0, 0, 0), -1)
        cv2.circle(frame, (220, 80), 35, (0, 0, 255), -1)
        cv2.line(frame, (50, 200), (280, 160), (255, 0, 0), 4)
        cv2.putText(
            frame,
            "SKYEYES",
            (90, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 120, 0),
            2
        )

        return frame

    def _shift_frame(self, frame, dx, dy):
        transform = np.float32([
            [1, 0, dx],
            [0, 1, dy],
        ])

        height, width = frame.shape[:2]

        return cv2.warpAffine(
            frame,
            transform,
            (width, height),
            borderMode=cv2.BORDER_REFLECT
        )


if __name__ == "__main__":
    unittest.main()
