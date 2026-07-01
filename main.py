import cv2

from config import *
from camera.receiver import CameraReceiver
from ui.display import Display
from utils.fps import FPS


def main():

    camera = CameraReceiver(CAMERA_SOURCE)

    display = Display(WINDOW_NAME)

    fps_counter = FPS()

    while True:

        frame = camera.read()

        if frame is None:
            break

        fps = fps_counter.get()

        display.show(frame, fps)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    camera.release()

    display.close()


if __name__ == "__main__":
    main()