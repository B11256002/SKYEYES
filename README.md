# SKYEYES

Sky-based Agricultural Monitoring System

## Introduction

SKYEYES is a balloon-based aerial monitoring system designed for agricultural field surveillance.

The system receives real-time images from an ESP32-S3-CAM or a video source, performs object detection using YOLOv8-OBB, and checks whether detected objects enter a predefined boundary area.

## Current Version

V0.5 Alarm Module

## Current Features

- Modular project architecture
- Camera or video frame receiver
- YOLOv8-OBB detection pipeline
- Detection data model
- FPS calculation
- OpenCV display with OBB, label, confidence, center point, and boundary status
- Fixed polygon boundary manager
- Configurable frame resizing for smaller display windows
- ArUco marker landmark detection with marker ID and center point display
- Boundary alarm events with cooldown and on-screen alert banner

## Development Roadmap

- [x] V0.1 Project Architecture
- [x] V0.2 YOLOv8-OBB Detection
- [x] V0.3 Boundary Detection
- [x] V0.4 ArUco Landmark
- [x] V0.5 Alarm Module
- [ ] V0.6 ESP32 Communication
- [ ] V0.7 Object Tracking
- [ ] V0.8 Image Stabilization
- [ ] V1.0 SKYEYES Release

## Boundary Configuration

The V0.3 boundary is configured in `config.py`:

```python
BOUNDARY_POINTS = [
    (120, 120),
    (520, 120),
    (560, 420),
    (100, 420),
]
```

A detection is marked as `inside_boundary=True` when its center point is inside the polygon.

## Frame Size Configuration

The video frame width is configured in `config.py`:

```python
FRAME_WIDTH = 960
```

Frames wider than this value are resized while preserving the original aspect ratio. Smaller frames are kept unchanged.

## ArUco Landmark Configuration

The ArUco dictionary is configured in `config.py`:

```python
ARUCO_DICTIONARY = "DICT_4X4_50"
```

Detected markers are converted into `Landmark` objects containing marker ID, four corners, and center point. V0.4 displays these markers on the frame; later versions can use them to adjust the boundary position dynamically.

ArUco markers are not arbitrary black-and-white images. Each marker must match a specific ID inside a specific dictionary. This project currently uses `DICT_4X4_50`, so printed markers should be generated from the same dictionary.

Generate the default test marker:

```powershell
python tools\generate_aruco.py --id 7 --size 800
```

The generated image is saved to:

```text
assets/aruco/aruco_dict_4x4_50_id_7.png
```

Print the image clearly on flat paper, keep the black border visible, and avoid cutting off the marker edge.

## Alarm Configuration

V0.5 creates alarm events when a detection enters the configured boundary. The cooldown prevents repeated alerts from flooding the console and display:

```python
ALARM_COOLDOWN_SECONDS = 2.0
```

The current alarm output is a console message and an on-screen red alert banner. Later versions can extend the same `AlarmEvent` model to MQTT, Line Notify, email, or local log files.
