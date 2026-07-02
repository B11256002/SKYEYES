from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

CAMERA_SOURCE = str(PROJECT_ROOT / "videos" / "test.mp4")
MODEL_PATH = str(PROJECT_ROOT / "models" / "best.pt")

WINDOW_NAME = "SKYEYES"
CONFIDENCE = 0.4

BOUNDARY_POINTS = [
    (120, 120),
    (520, 120),
    (560, 420),
    (100, 420),
]
