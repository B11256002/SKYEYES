import cv2

class CameraReceiver:

    def __init__(self, source=0):

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception("Camera Open Failed")

    def read(self):

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def release(self):

        self.cap.release()