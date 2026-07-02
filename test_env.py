import sys
import cv2

print("Python:", sys.executable)
print("OpenCV file:", cv2.__file__)

try:
    print("OpenCV version:", cv2.__version__)
except Exception as e:
    print("Version error:", e)