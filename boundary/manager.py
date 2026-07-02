import cv2
import numpy as np


class BoundaryManager:

    def __init__(self, points):
        if len(points) < 3:
            raise ValueError("Boundary needs at least 3 points.")

        self.points = [(int(x), int(y)) for x, y in points]
        self._polygon = np.array(self.points, dtype=np.int32)

    def contains(self, point):
        return cv2.pointPolygonTest(self._polygon, point, False) >= 0

    def update(self, detections):
        for detection in detections:
            detection.inside_boundary = self.contains(detection.center)

        return detections
