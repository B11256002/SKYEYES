import cv2

from config import *
from camera.receiver import CameraReceiver
from ui.display import Display
from utils.fps import FPS
from detection.yolo import YOLODetector
from boundary.manager import BoundaryManager
from landmark.aruco import ArUcoLandmarkDetector
from alarm.manager import AlarmManager
from communication.factory import create_esp32_communicator
from communication.protocol import make_command
from tracking.centroid import CentroidTracker
from stabilization.image import ImageStabilizer
from core.system_status import SystemStatus


def main():

    camera = CameraReceiver(
        CAMERA_SOURCE,
        FRAME_WIDTH,
        VIDEO_REALTIME_PLAYBACK
    )

    detector = YOLODetector(
        MODEL_PATH,
        CONFIDENCE,
        YOLO_DEVICE,
        YOLO_IMAGE_SIZE,
        YOLO_HALF
    )

    display = Display(WINDOW_NAME)

    boundary = BoundaryManager(BOUNDARY_POINTS)

    landmark_detector = ArUcoLandmarkDetector(ARUCO_DICTIONARY)

    alarm_manager = AlarmManager(ALARM_COOLDOWN_SECONDS)

    tracker = CentroidTracker(TRACKING_MAX_DISTANCE, TRACKING_MAX_MISSING)

    stabilizer = ImageStabilizer(
        STABILIZATION_ENABLED,
        STABILIZATION_MAX_FEATURES,
        STABILIZATION_MIN_MATCHES
    )

    esp32 = create_esp32_communicator(
        ESP32_ENABLED,
        ESP32_PORT,
        ESP32_BAUDRATE
    )
    esp32_status = esp32.connect()

    fps_counter = FPS()

    print(f"Camera source: {CAMERA_SOURCE}")
    print(f"Model path: {MODEL_PATH}")
    print(f"YOLO device: {YOLO_DEVICE}")
    print(f"YOLO image size: {YOLO_IMAGE_SIZE}")
    print(f"YOLO half precision: {YOLO_HALF}")
    print(f"Frame width: {FRAME_WIDTH}")
    print(f"Realtime video playback: {VIDEO_REALTIME_PLAYBACK}")
    print(f"Stabilization enabled: {STABILIZATION_ENABLED}")
    print(f"ESP32 status: {esp32_status.message}")

    while True:
        frame = camera.read()

        if frame is None:
            break

        frame = stabilizer.stabilize(frame)

        detections = detector.detect(frame)

        detections = tracker.update(detections)

        detections = boundary.update(detections)

        landmarks = landmark_detector.detect(frame)

        alarm_events = alarm_manager.update(detections)

        for event in alarm_events:
            print(event.message)
            esp32.send(make_command("ALARM", event.message))

        fps = fps_counter.get()
        latest_alarm = "\u7121\u8b66\u5831"

        if alarm_manager.latest_event is not None:
            latest_alarm = alarm_manager.latest_event.message

        status = SystemStatus(
            fps=fps,
            detections_count=len(detections),
            inside_boundary_count=sum(det.inside_boundary for det in detections),
            landmarks_count=len(landmarks),
            active_tracks_count=len(tracker.tracks),
            esp32_mode=esp32_status.mode,
            stabilization_enabled=STABILIZATION_ENABLED,
            latest_alarm=latest_alarm
        )

        display.draw_boundary(frame, boundary.points)

        display.draw_landmarks(frame, landmarks)

        display.draw(frame, detections)

        display.draw_alarm(frame, alarm_manager.latest_event)

        display.show(frame, fps, status)

        if cv2.waitKey(1) == ord("q"):
            break

    camera.release()
    esp32.close()

    display.close()


if __name__ == "__main__":
    main()
