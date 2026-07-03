# SKYEYES

Sky-based Agricultural Monitoring System

## Introduction

SKYEYES is a balloon-based aerial monitoring system designed for agricultural field surveillance.

The system receives real-time images from an ESP32-S3-CAM or a video source, performs object detection using YOLOv8-OBB, and checks whether detected objects enter a predefined boundary area.

## Current Version

V0.9 System UI Overlay

## Local Setup

For local installation and startup instructions, see [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md).

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
- ESP32 communication protocol with serial and mock modes
- Centroid-based object tracking with stable detection IDs
- Feature-based image stabilization before detection
- OpenCV system dashboard with FPS, detections, tracks, landmarks, ESP32 status, and latest alarm

## Development Roadmap

- [x] V0.1 Project Architecture
- [x] V0.2 YOLOv8-OBB Detection
- [x] V0.3 Boundary Detection
- [x] V0.4 ArUco Landmark
- [x] V0.5 Alarm Module
- [x] V0.6 ESP32 Communication
- [x] V0.7 Object Tracking
- [x] V0.8 Image Stabilization
- [x] V0.9 System UI Overlay
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

## YOLO Device Configuration

YOLO inference device is configured in `config.py`:

```python
YOLO_DEVICE = "cuda"
YOLO_IMAGE_SIZE = 640
YOLO_HALF = False
VISION_PROCESS_INTERVAL = 10
RUNTIME_TARGET_FPS = 10
WEB_STREAM_FPS = 10
WEB_JPEG_QUALITY = 70
```

Use `"cuda"` for NVIDIA GPU inference and `"cpu"` for CPU inference. Check whether the current Python environment can access CUDA:

```powershell
python tools\check_gpu.py
```

If CUDA is not available, install a CUDA-enabled PyTorch build in the same Python environment used to run `main.py`.

For better real-time performance, the default display width is reduced and image stabilization is disabled:

```python
FRAME_WIDTH = 800
VIDEO_REALTIME_PLAYBACK = True
STABILIZATION_ENABLED = False
```

Increase these values only when image detail or stabilization is more important than FPS.

When testing with a video file, `VIDEO_REALTIME_PLAYBACK` skips delayed frames so playback follows real time instead of becoming slow motion. This is closer to the final ESP32 live stream behavior, where the system should process the newest available frame.

`VISION_PROCESS_INTERVAL` controls how often the heavy vision pipeline runs. The default value `10` means YOLO, tracking, boundary checks, ArUco detection, and alarm updates run once every 10 frames while the video still plays every frame. Lower it for faster alert response, or raise it to reduce CPU usage further.

`RUNTIME_TARGET_FPS` caps the backend frame loop itself. This prevents the system from using extra CPU just to decode, resize, draw, or encode frames faster than the monitor view needs. For the web console, `WEB_STREAM_FPS` caps how often JPEG frames are encoded and sent to the browser. `WEB_JPEG_QUALITY` controls MJPEG compression quality. Lower values reduce CPU usage and bandwidth at the cost of visual detail.

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

## ESP32 Communication Configuration

V0.6 adds a PC-to-ESP32 command channel. The project defaults to mock mode, so the system can still be tested with video only when no ESP32 or webcam is available:

```python
ESP32_ENABLED = False
ESP32_PORT = "COM3"
ESP32_BAUDRATE = 115200
```

When `ESP32_ENABLED` is `False`, commands are recorded by `MockESP32Communicator` and no serial port is opened. When hardware is available, set `ESP32_ENABLED = True` and update `ESP32_PORT`.

Commands are sent as one-line JSON messages:

```json
{"command":"ALARM","value":"person entered boundary"}
```

In V0.6, alarm events send an `ALARM` command to the ESP32 communication layer. Future firmware can interpret this command to trigger buzzer, LED, or telemetry behavior.

## Tracking Configuration

V0.7 adds a lightweight centroid tracker. It assigns stable IDs to detections by matching each new detection to the nearest previous track with the same label:

```python
TRACKING_MAX_DISTANCE = 80
TRACKING_MAX_MISSING = 10
```

Tracked detections display `ID n` on the frame. Alarm cooldown also uses `tracked_id`, so moving objects are handled more consistently than using center point alone. This is a simple tracker designed for the current video-only workflow; later versions can replace it with ByteTrack or DeepSORT if stronger tracking is needed.

## Image Stabilization Configuration

V0.8 adds feature-based image stabilization before YOLO detection. The first frame is used as the reference frame, and later frames are aligned with ORB feature matching and affine transform estimation:

```python
STABILIZATION_ENABLED = True
STABILIZATION_MAX_FEATURES = 500
STABILIZATION_MIN_MATCHES = 12
```

If there are not enough visual features or the transform cannot be estimated, the original frame is used. This keeps video-only testing stable even when a frame cannot be corrected.

## System UI Overlay

V0.9 adds a right-side dashboard to the OpenCV display. The panel shows live system status without covering the video frame:

- FPS
- Detection count
- Boundary intrusion count
- ArUco landmark count
- Active tracking IDs
- ESP32 communication mode
- Stabilization status
- Latest alarm message

This keeps the current video-only workflow simple while making the system easier to present and monitor.

## Web Interface

The experimental web console runs on a separate branch and keeps the OpenCV version intact. Start it from the project root:

```powershell
D:\Tool\Anaconda\envs\skyeyes\python.exe -m webapp.server
```

Then open:

```text
http://127.0.0.1:5000
```

The web console provides:

- MJPEG live video stream
- Real-time FPS, detection, tracking, landmark, and ESP32 status
- Latest alarm panel
- Alarm history list

The backend still uses the same Python YOLO pipeline, so GPU, frame size, and realtime playback settings remain controlled by `config.py`.
