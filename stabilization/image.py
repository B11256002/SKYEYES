import cv2
import numpy as np


class ImageStabilizer:

    def __init__(self, enabled=True, max_features=500, min_matches=12):
        self.enabled = enabled
        self.min_matches = min_matches
        self.reference_gray = None
        self.reference_keypoints = None
        self.reference_descriptors = None
        self.orb = cv2.ORB_create(max_features)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def stabilize(self, frame):
        if not self.enabled:
            return frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)

        if self.reference_gray is None:
            self._set_reference(gray, keypoints, descriptors)
            return frame

        if descriptors is None or self.reference_descriptors is None:
            return frame

        matches = self.matcher.match(descriptors, self.reference_descriptors)

        if len(matches) < self.min_matches:
            return frame

        matches = sorted(matches, key=lambda match: match.distance)
        matches = matches[:80]

        current_points = np.float32([
            keypoints[match.queryIdx].pt
            for match in matches
        ])
        reference_points = np.float32([
            self.reference_keypoints[match.trainIdx].pt
            for match in matches
        ])

        transform, _ = cv2.estimateAffinePartial2D(
            current_points,
            reference_points,
            method=cv2.RANSAC
        )

        if transform is None:
            return frame

        height, width = frame.shape[:2]

        return cv2.warpAffine(
            frame,
            transform,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT
        )

    def reset(self):
        self.reference_gray = None
        self.reference_keypoints = None
        self.reference_descriptors = None

    def _set_reference(self, gray, keypoints, descriptors):
        self.reference_gray = gray
        self.reference_keypoints = keypoints
        self.reference_descriptors = descriptors
