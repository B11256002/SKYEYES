import cv2

from config import *
from camera.receiver import CameraReceiver
from ui.display import Display
from utils.fps import FPS
from detection.yolo import YOLODetector
from boundary.manager import BoundaryManager
from landmark.aruco import ArUcoLandmarkDetector
from alarm.manager import AlarmManager


def main():

    camera = CameraReceiver(CAMERA_SOURCE, FRAME_WIDTH)

    detector = YOLODetector(MODEL_PATH, CONFIDENCE)

    display = Display(WINDOW_NAME)

    boundary = BoundaryManager(BOUNDARY_POINTS)

    landmark_detector = ArUcoLandmarkDetector(ARUCO_DICTIONARY)

    alarm_manager = AlarmManager(ALARM_COOLDOWN_SECONDS)

    fps_counter = FPS()

    print(f"Camera source: {CAMERA_SOURCE}")
    print(f"Model path: {MODEL_PATH}")
    print(f"Frame width: {FRAME_WIDTH}")

    while True:

        frame = camera.read()

        if frame is None:
            break

        detections = detector.detect(frame)

        detections = boundary.update(detections)

        landmarks = landmark_detector.detect(frame)

        alarm_events = alarm_manager.update(detections)

        for event in alarm_events:
            print(event.message)

        fps = fps_counter.get()

        display.draw_boundary(frame, boundary.points)

        display.draw_landmarks(frame, landmarks)

        display.draw(frame, detections)

        display.draw_alarm(frame, alarm_manager.latest_event)

        display.show(frame, fps)

        if cv2.waitKey(1) == ord("q"):
            break

    camera.release()

    display.close()


if __name__ == "__main__":
    main()
