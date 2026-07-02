import cv2
import numpy as np


class Display:

    def __init__(self, window_name):
        self.window_name = window_name

    def draw_boundary(self, frame, points):
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], color=(0, 180, 255))
        cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)

        cv2.polylines(
            frame,
            [pts],
            isClosed=True,
            color=(0, 180, 255),
            thickness=2
        )

        cv2.putText(
            frame,
            "BOUNDARY",
            tuple(pts[0][0]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 180, 255),
            2
        )

    def draw(self, frame, detections):
        for det in detections:
            pts = np.array(det.corners, dtype=np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if det.inside_boundary else (0, 255, 0)
            status = "INSIDE" if det.inside_boundary else "OUTSIDE"

            cv2.polylines(
                frame,
                [pts],
                isClosed=True,
                color=color,
                thickness=2
            )

            cv2.circle(
                frame,
                det.center,
                4,
                color,
                -1
            )

            x = int(pts[0][0][0])
            y = int(pts[0][0][1]) - 10

            cv2.putText(
                frame,
                f"{det.label} {det.confidence:.2f} {status}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

    def draw_landmarks(self, frame, landmarks):
        for landmark in landmarks:
            pts = np.array(landmark.corners, dtype=np.int32).reshape((-1, 1, 2))

            cv2.polylines(
                frame,
                [pts],
                isClosed=True,
                color=(255, 0, 0),
                thickness=2
            )

            cv2.circle(
                frame,
                landmark.center,
                4,
                (255, 0, 0),
                -1
            )

            label_position = (
                int(landmark.center[0]) + 8,
                int(landmark.center[1]) - 8
            )

            cv2.putText(
                frame,
                f"ID {landmark.marker_id}",
                label_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

    def show(self, frame, fps):
        cv2.putText(
            frame,
            f"FPS : {fps:.2f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow(self.window_name, frame)

    def close(self):
        cv2.destroyAllWindows()
