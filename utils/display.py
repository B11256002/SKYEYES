import cv2

class Display:

    def __init__(self, window_name):

        self.window_name = window_name

    def show(self, frame, fps):

        cv2.putText(
            frame,
            f"FPS : {fps:.2f}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        cv2.imshow(self.window_name, frame)

    def close(self):

        cv2.destroyAllWindows()