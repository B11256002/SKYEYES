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
        self.lifecycle_lock = threading.RLock()
        self.thread = None
        self.stop_event = threading.Event()
        self.latest_jpeg = None
        self.status = self._empty_status()
        self.alarms = deque(maxlen=30)
        self.error = None
        self.source_config = self._build_source_config("video", CAMERA_SOURCE)

    def start(self):
        with self.lifecycle_lock:
            if self.thread and self.thread.is_alive():
                return

            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        with self.lifecycle_lock:
            self.stop_event.set()

            if self.thread:
                self.thread.join(timeout=2)
                self.thread = None

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
                "source": dict(self.source_config),
            }

    def get_alarms(self):
        with self.lock:
            return list(self.alarms)

    def get_source(self):
        with self.lock:
            return dict(self.source_config)

    def set_source(self, mode, value=None):
        next_config = self._build_source_config(mode, value)

        with self.lock:
            current_config = dict(self.source_config)

        if (
            current_config["mode"] == next_config["mode"]
            and current_config["value"] == next_config["value"]
        ):
            return next_config

        self.stop()

        with self.lock:
            self.source_config = next_config
            self.latest_jpeg = None
            self.status = self._empty_status()
            self.error = "\u5f71\u50cf\u4f86\u6e90\u5207\u63db\u4e2d"

        self.start()

        return next_config

    def _run(self):
        camera = None
        esp32 = None

        try:
            source_config = self.get_source()
            camera = CameraReceiver(
                source_config["source"],
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
            frame_index = 0
            process_interval = max(1, int(VISION_PROCESS_INTERVAL))
            target_interval = 1.0 / max(1, int(RUNTIME_TARGET_FPS))
            detections = []
            landmarks = []
            stream_interval = 1.0 / max(1, int(WEB_STREAM_FPS))
            last_stream_time = 0

            while not self.stop_event.is_set():
                loop_started = time.time()
                frame = camera.read()

                if frame is None:
                    break

                frame_index += 1
                should_process = (
                    frame_index == 1
                    or (frame_index - 1) % process_interval == 0
                )

                frame = stabilizer.stabilize(frame)

                if should_process:
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

                now = time.time()

                with self.lock:
                    self.status = status
                    self.error = None

                if now - last_stream_time < stream_interval:
                    self._sleep_until_next_frame(loop_started, target_interval)
                    continue

                last_stream_time = now
                ok, encoded = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), WEB_JPEG_QUALITY]
                )

                if ok:
                    with self.lock:
                        self.latest_jpeg = encoded.tobytes()

                self._sleep_until_next_frame(loop_started, target_interval)

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

    def _sleep_until_next_frame(self, loop_started, target_interval):
        elapsed = time.time() - loop_started

        if elapsed < target_interval:
            time.sleep(target_interval - elapsed)

    def _build_source_config(self, mode, value=None):
        normalized_mode = (mode or "video").strip().lower()

        if normalized_mode == "video":
            source = CAMERA_SOURCE
            display_value = str(CAMERA_SOURCE)
            label = "\u6e2c\u8a66\u5f71\u7247"
        elif normalized_mode == "webcam":
            source = self._parse_camera_index(value, 0)
            display_value = str(source)
            label = f"Webcam {source}"
        elif normalized_mode == "custom":
            display_value = str(value or "").strip()

            if not display_value:
                raise ValueError("\u8acb\u8f38\u5165\u81ea\u8a02\u5f71\u50cf\u4f86\u6e90")

            source = self._parse_custom_source(display_value)
            label = "\u81ea\u8a02\u4f86\u6e90"
        else:
            raise ValueError("\u4e0d\u652f\u63f4\u7684\u5f71\u50cf\u4f86\u6e90")

        return {
            "mode": normalized_mode,
            "value": display_value,
            "source": source,
            "label": label,
        }

    def _parse_camera_index(self, value, default):
        if value in (None, ""):
            return default

        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Webcam \u7de8\u865f\u5fc5\u9808\u662f\u6578\u5b57") from exc

    def _parse_custom_source(self, value):
        try:
            return int(value)
        except ValueError:
            return value

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
