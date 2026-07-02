import cv2

from config import *
from camera.receiver import CameraReceiver
from ui.display import Display
from utils.fps import FPS
from detection.yolo import YOLODetector


def main():

    camera = CameraReceiver(CAMERA_SOURCE)

    detector = YOLODetector(MODEL_PATH)

    display = Display(WINDOW_NAME)

    fps_counter = FPS()

    print(CAMERA_SOURCE)

    while True:

        frame = camera.read()

        if frame is None:
            break

        detections = detector.detect(frame)

        for det in detections:
            print(det)

        fps = fps_counter.get()

        display.draw(frame, detections)

        display.show(frame, fps)

        if cv2.waitKey(1) == ord("q"):
            break

        print(detections)

       # print(f"Found {len(detections)} detections")
       # print(f"Detection Count: {len(detections)}")

    camera.release()

    display.close()


if __name__ == "__main__":
    main()