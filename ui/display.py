import cv2
import numpy as np


class Display:

    def __init__(self, window_name):
        self.window_name = window_name

    def draw(self, frame, detections):

        for det in detections:

            # 四個角點
            pts = np.array(det.corners, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))

            # 畫 OBB
            cv2.polylines(
                frame,
                [pts],
                isClosed=True,
                color=(255, 255, 0),      # 青色
                thickness=2
            )

            # 中心點
            cv2.circle(
                frame,
                det.center,
                4,
                (0, 0, 255),              # 紅色
                -1
            )

            # 標籤
            x = pts[0][0][0]
            y = pts[0][0][1] - 10

            cv2.putText(
                frame,
                f"{det.label} {det.confidence:.2f}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
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