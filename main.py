import cv2

from config import *
from camera.receiver import CameraReceiver
from ui.display import Display
from utils.fps import FPS
from detection.yolo import YOLODetector
from boundary.manager import BoundaryManager


def main():

    camera = CameraReceiver(CAMERA_SOURCE)

    detector = YOLODetector(MODEL_PATH, CONFIDENCE)

    display = Display(WINDOW_NAME)

    boundary = BoundaryManager(BOUNDARY_POINTS)

    fps_counter = FPS()

    print(f"Camera source: {CAMERA_SOURCE}")
    print(f"Model path: {MODEL_PATH}")

    while True:

        frame = camera.read()

        if frame is None:
            break

        detections = detector.detect(frame)

        detections = boundary.update(detections)

        for det in detections:
            if det.inside_boundary:
                print(f"Boundary event: {det.label} at {det.center}")

        fps = fps_counter.get()

        display.draw_boundary(frame, boundary.points)

        display.draw(frame, detections)

        display.show(frame, fps)

        if cv2.waitKey(1) == ord("q"):
            break

    camera.release()

    display.close()


if __name__ == "__main__":
    main()
