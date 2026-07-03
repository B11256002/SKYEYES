import threading
import time
from collections import deque

import cv2

from alarm.manager import AlarmManager
from boundary.manager import BoundaryManager
from camera.receiver import CameraReceiver
from communication.factory import create_esp32_communicator
from communication.protocol import make_command
from config import *
from core.system_status import SystemStatus
from detection.yolo import YOLODetector
from landmark.aruco import ArUcoLandmarkDetector
from stabilization.image import ImageStabilizer
from tracking.centroid import CentroidTracker
from ui.display import Display
from utils.fps import FPS


class SkyEyesRuntime:

    def __init__(self):
        self.lock = threading.Lock()
        self.thread = None
        self.stop_event = threading.Event()
        self.latest_jpeg = None
        self.status = self._empty_status()
        self.alarms = deque(maxlen=30)
        self.error = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

        if self.thread:
            self.thread.join(timeout=2)

    def get_frame(self):
        with self.lock:
            return self.latest_jpeg

    def get_status(self):
        with self.lock:
            status = self.status

            return {
                "fps": round(status.fps, 2),
                "detections_count": status.detections_count,
                "inside_boundary_count": status.inside_boundary_count,
                "landmarks_count": status.landmarks_count,
                "active_tracks_count": status.active_tracks_count,
                "esp32_mode": status.esp32_mode,
                "stabilization_enabled": status.stabilization_enabled,
                "latest_alarm": status.latest_alarm,
                "error": self.error,
            }

    def get_alarms(self):
        with self.lock:
            return list(self.alarms)

    def _run(self):
        camera = None
        esp32 = None

        try:
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
            overlay = Display(WINDOW_NAME)
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

            while not self.stop_event.is_set():
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
                    esp32.send(make_command("ALARM", event.message))
                    self._add_alarm(event.message)

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

                overlay.draw_boundary(frame, boundary.points)
                overlay.draw_landmarks(frame, landmarks)
                overlay.draw(frame, detections)
                overlay.draw_alarm(frame, alarm_manager.latest_event)

                ok, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 82]
                )

                if ok:
                    with self.lock:
                        self.latest_jpeg = encoded.tobytes()
                        self.status = status
                        self.error = None

        except Exception as exc:
            with self.lock:
                self.error = str(exc)

        finally:
            if camera is not None:
                camera.release()

            if esp32 is not None:
                esp32.close()

    def _add_alarm(self, message):
        self.alarms.appendleft({
            "time": time.strftime("%H:%M:%S"),
            "message": message,
        })

    def _empty_status(self):
        return SystemStatus(
            fps=0,
            detections_count=0,
            inside_boundary_count=0,
            landmarks_count=0,
            active_tracks_count=0,
            esp32_mode="offline",
            stabilization_enabled=STABILIZATION_ENABLED,
        )
