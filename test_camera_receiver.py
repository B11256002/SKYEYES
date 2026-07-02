import unittest

import numpy as np

from camera.receiver import CameraReceiver


class CameraReceiverResizeTest(unittest.TestCase):

    def test_resize_preserves_aspect_ratio(self):
        receiver = CameraReceiver.__new__(CameraReceiver)
        receiver.frame_width = 960
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        resized = receiver._resize(frame)

        self.assertEqual(resized.shape[:2], (540, 960))

    def test_resize_keeps_smaller_frame(self):
        receiver = CameraReceiver.__new__(CameraReceiver)
        receiver.frame_width = 960
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        resized = receiver._resize(frame)

        self.assertEqual(resized.shape[:2], (480, 640))


if __name__ == "__main__":
    unittest.main()
