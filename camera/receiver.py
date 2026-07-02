import time

import cv2


class CameraReceiver:

    def __init__(self, source=0, frame_width=None, realtime=False):

        self.source = source
        self.frame_width = frame_width
        self.realtime = realtime
        self.cap = cv2.VideoCapture(source)
        self.source_fps = self.cap.get(cv2.CAP_PROP_FPS) or 0
        self.frame_index = 0
        self.start_time = None

        if not self.cap.isOpened():
            raise Exception(f"Cannot open source: {source}")

    def read(self):

        self._sync_video_time()

        ret, frame = self.cap.read()

        if not ret:
            return None

        self.frame_index += 1

        return self._resize(frame)

    def release(self):

        self.cap.release()

    def _sync_video_time(self):
        if not self.realtime or self.source_fps <= 1:
            return

        if self.start_time is None:
            self.start_time = time.time()
            return

        elapsed = time.time() - self.start_time
        target_index = int(elapsed * self.source_fps)
        frames_to_skip = target_index - self.frame_index

        for _ in range(max(0, frames_to_skip)):
            if not self.cap.grab():
                return

            self.frame_index += 1

    def _resize(self, frame):
        if self.frame_width is None:
            return frame

        height, width = frame.shape[:2]

        if width <= self.frame_width:
            return frame

        scale = self.frame_width / width
        frame_height = int(height * scale)

        return cv2.resize(
            frame,
            (self.frame_width, frame_height),
            interpolation=cv2.INTER_AREA
        )
