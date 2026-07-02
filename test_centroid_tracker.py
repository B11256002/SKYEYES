import unittest

from core.detection import Detection
from tracking.centroid import CentroidTracker


class CentroidTrackerTest(unittest.TestCase):

    def test_keeps_same_id_for_nearby_detection(self):
        tracker = CentroidTracker(max_distance=50, max_missing=2)

        first = tracker.update([self._detection(center=(100, 100))])
        second = tracker.update([self._detection(center=(120, 110))])

        self.assertEqual(first[0].tracked_id, 1)
        self.assertEqual(second[0].tracked_id, 1)

    def test_assigns_different_ids_to_two_detections(self):
        tracker = CentroidTracker(max_distance=50, max_missing=2)

        detections = tracker.update([
            self._detection(center=(100, 100)),
            self._detection(center=(300, 100)),
        ])

        self.assertEqual([det.tracked_id for det in detections], [1, 2])

    def test_creates_new_id_when_detection_is_too_far(self):
        tracker = CentroidTracker(max_distance=50, max_missing=2)

        first = tracker.update([self._detection(center=(100, 100))])
        second = tracker.update([self._detection(center=(300, 100))])

        self.assertEqual(first[0].tracked_id, 1)
        self.assertEqual(second[0].tracked_id, 2)

    def test_removes_missing_tracks_after_limit(self):
        tracker = CentroidTracker(max_distance=50, max_missing=1)

        tracker.update([self._detection(center=(100, 100))])
        tracker.update([])
        tracker.update([])

        self.assertEqual(tracker.tracks, {})

    def _detection(self, center, label="person"):
        x, y = center

        return Detection(
            label=label,
            confidence=0.9,
            corners=[
                (x - 10, y - 10),
                (x + 10, y - 10),
                (x + 10, y + 10),
                (x - 10, y + 10),
            ],
            center=center,
            timestamp=0.0
        )


if __name__ == "__main__":
    unittest.main()
