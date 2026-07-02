import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class Display:

    def __init__(self, window_name):
        self.window_name = window_name
        self.panel_width = 320
        self.font_path = "C:/Windows/Fonts/msjh.ttc"
        self.font_cache = {}

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

        self._put_text(
            frame,
            "邊界",
            int(pts[0][0][0]),
            int(pts[0][0][1]),
            22,
            (0, 180, 255)
        )

    def draw(self, frame, detections):
        for det in detections:
            pts = np.array(det.corners, dtype=np.int32).reshape((-1, 1, 2))
            color = (0, 0, 255) if det.inside_boundary else (0, 255, 0)
            status = "界內" if det.inside_boundary else "界外"

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
            track_label = ""

            if det.tracked_id != -1:
                track_label = f" ID {det.tracked_id}"

            self._put_text(
                frame,
                f"{det.label}{track_label} {det.confidence:.2f} {status}",
                x,
                y,
                20,
                color
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

            self._put_text(
                frame,
                f"地標 ID {landmark.marker_id}",
                int(landmark.center[0]) + 8,
                int(landmark.center[1]) - 8,
                20,
                (255, 0, 0)
            )

    def draw_alarm(self, frame, alarm_event):
        if alarm_event is None:
            return

        height, width = frame.shape[:2]
        banner_height = 46

        cv2.rectangle(
            frame,
            (0, 0),
            (width, banner_height),
            (0, 0, 180),
            -1
        )

        self._put_text(frame, alarm_event.message, 16, 10, 22, (255, 255, 255))

    def draw_dashboard(self, frame, status):
        height = frame.shape[0]
        panel = np.full(
            (height, self.panel_width, 3),
            (28, 31, 36),
            dtype=np.uint8
        )

        cv2.rectangle(
            panel,
            (0, 0),
            (self.panel_width, 54),
            (20, 96, 130),
            -1
        )

        self._put_panel_text(panel, "SKYEYES", 18, 36, 26, (255, 255, 255))
        self._put_panel_text(panel, "系統監控", 18, 76, 18, (190, 210, 220))

        rows = [
            ("FPS", f"{status.fps:.2f}"),
            ("偵測數", str(status.detections_count)),
            ("界內數", str(status.inside_boundary_count)),
            ("地標數", str(status.landmarks_count)),
            ("追蹤數", str(status.active_tracks_count)),
            ("ESP32", status.esp32_mode),
            ("穩定器", "開啟" if status.stabilization_enabled else "關閉"),
        ]

        y = 112

        for label, value in rows:
            self._draw_status_row(panel, label, value, y)
            y += 36

        self._draw_latest_alarm(panel, status.latest_alarm, y + 10, height)

        return np.hstack((frame, panel))

    def show(self, frame, fps, status=None):
        self._put_text(frame, f"FPS：{fps:.2f}", 20, 56, 24, (0, 255, 0))

        if status is not None:
            frame = self.draw_dashboard(frame, status)

        cv2.imshow(self.window_name, frame)

    def close(self):
        cv2.destroyAllWindows()

    def _draw_status_row(self, panel, label, value, y):
        cv2.rectangle(
            panel,
            (16, y - 22),
            (self.panel_width - 16, y + 8),
            (42, 47, 54),
            -1
        )

        self._put_panel_text(panel, label, 28, y, 17, (185, 190, 195))
        self._put_panel_text(panel, value, 178, y, 18, (245, 245, 245))

    def _draw_latest_alarm(self, panel, latest_alarm, y, panel_height):
        bottom = panel_height - 16

        if bottom <= y + 48:
            return

        alarm_color = (80, 80, 220)

        if latest_alarm == "無警報":
            alarm_color = (70, 130, 70)

        cv2.rectangle(
            panel,
            (16, y),
            (self.panel_width - 16, bottom),
            alarm_color,
            -1
        )
        self._put_panel_text(panel, "最新警報", 28, y + 28, 17, (255, 255, 255))
        self._put_wrapped_text(
            panel,
            latest_alarm,
            28,
            y + 46,
            self.panel_width - 56,
            16,
            (255, 255, 255),
            bottom
        )

    def _put_panel_text(self, image, text, x, y, font_size, color):
        self._put_text(image, text, x, y - font_size, font_size, color)

    def _put_wrapped_text(self, image, text, x, y, max_width, font_size, color, max_y):
        words = str(text).split()
        line = ""
        line_height = font_size + 8

        for word in words:
            candidate = word if not line else f"{line} {word}"
            size = self._text_size(candidate, font_size)

            if size[0] <= max_width:
                line = candidate
                continue

            if y + line_height > max_y:
                return

            self._put_text(image, line, x, y, font_size, color)
            y += line_height
            line = word

        if line and y + line_height <= max_y:
            self._put_text(image, line, x, y, font_size, color)

    def _put_text(self, image, text, x, y, font_size, color):
        font = self._font(font_size)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        draw = ImageDraw.Draw(pil_image)
        rgb_color = (color[2], color[1], color[0])

        draw.text(
            (x, y),
            str(text),
            font=font,
            fill=rgb_color
        )

        image[:] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def _text_size(self, text, font_size):
        font = self._font(font_size)
        bbox = font.getbbox(str(text))

        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def _font(self, font_size):
        if font_size in self.font_cache:
            return self.font_cache[font_size]

        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except OSError:
            font = ImageFont.load_default()

        self.font_cache[font_size] = font

        return font
