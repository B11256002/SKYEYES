import math


class CentroidTracker:

    def __init__(self, max_distance=80, max_missing=10):
        self.max_distance = max_distance
        self.max_missing = max_missing
        self.next_id = 1
        self.tracks = {}

    def update(self, detections):
        unmatched_track_ids = set(self.tracks.keys())

        for detection in detections:
            track_id = self._find_best_track(detection, unmatched_track_ids)

            if track_id is None:
                track_id = self._create_track(detection)
            else:
                unmatched_track_ids.remove(track_id)
                self._update_track(track_id, detection)

            detection.tracked_id = track_id

        for track_id in unmatched_track_ids:
            self.tracks[track_id]["missing"] += 1

        self._remove_missing_tracks()

        return detections

    def _find_best_track(self, detection, candidate_ids):
        best_track_id = None
        best_distance = self.max_distance

        for track_id in candidate_ids:
            track = self.tracks[track_id]

            if track["label"] != detection.label:
                continue

            distance = self._distance(track["center"], detection.center)

            if distance <= best_distance:
                best_distance = distance
                best_track_id = track_id

        return best_track_id

    def _create_track(self, detection):
        track_id = self.next_id
        self.next_id += 1

        self.tracks[track_id] = {
            "label": detection.label,
            "center": detection.center,
            "missing": 0,
        }

        return track_id

    def _update_track(self, track_id, detection):
        self.tracks[track_id]["center"] = detection.center
        self.tracks[track_id]["missing"] = 0

    def _remove_missing_tracks(self):
        expired_ids = [
            track_id
            for track_id, track in self.tracks.items()
            if track["missing"] > self.max_missing
        ]

        for track_id in expired_ids:
            del self.tracks[track_id]

    def _distance(self, point_a, point_b):
        return math.hypot(
            point_a[0] - point_b[0],
            point_a[1] - point_b[1]
        )
