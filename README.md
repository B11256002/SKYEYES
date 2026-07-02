# SKYEYES

Sky-based Agricultural Monitoring System

## Introduction

SKYEYES is a balloon-based aerial monitoring system designed for agricultural field surveillance.

The system receives real-time images from an ESP32-S3-CAM or a video source, performs object detection using YOLOv8-OBB, and checks whether detected objects enter a predefined boundary area.

## Current Version

V0.3 Boundary Manager

## Current Features

- Modular project architecture
- Camera or video frame receiver
- YOLOv8-OBB detection pipeline
- Detection data model
- FPS calculation
- OpenCV display with OBB, label, confidence, center point, and boundary status
- Fixed polygon boundary manager

## Development Roadmap

- [x] V0.1 Project Architecture
- [x] V0.2 YOLOv8-OBB Detection
- [x] V0.3 Boundary Detection
- [ ] V0.4 ArUco Landmark
- [ ] V0.5 Alarm Module
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
