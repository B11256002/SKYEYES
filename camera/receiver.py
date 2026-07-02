import cv2


class CameraReceiver:

    def __init__(self, source=0, frame_width=None):

        self.source = source
        self.frame_width = frame_width
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception(f"Cannot open source: {source}")

    def read(self):

        ret, frame = self.cap.read()

        if not ret:
            return None

        return self._resize(frame)

    def release(self):

        self.cap.release()

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
