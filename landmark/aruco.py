import cv2

from core.landmark import Landmark


class ArUcoLandmarkDetector:

    def __init__(self, dictionary_name="DICT_4X4_50"):
        if not hasattr(cv2.aruco, dictionary_name):
            raise ValueError(f"Unknown ArUco dictionary: {dictionary_name}")

        dictionary_id = getattr(cv2.aruco, dictionary_name)
        dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        parameters = cv2.aruco.DetectorParameters()

        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    def detect(self, frame):
        corners_list, marker_ids, _ = self.detector.detectMarkers(frame)

        if marker_ids is None:
            return []

        landmarks = []

        for corners, marker_id in zip(corners_list, marker_ids.flatten()):
            points = [(int(x), int(y)) for x, y in corners[0]]
            center_x = int(sum(point[0] for point in points) / 4)
            center_y = int(sum(point[1] for point in points) / 4)

            landmarks.append(
                Landmark(
                    marker_id=int(marker_id),
                    corners=points,
                    center=(center_x, center_y)
                )
            )

        return landmarks
