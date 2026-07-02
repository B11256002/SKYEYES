from dataclasses import dataclass


@dataclass
class SystemStatus:

    fps: float
    detections_count: int
    inside_boundary_count: int
    landmarks_count: int
    active_tracks_count: int
    esp32_mode: str
    stabilization_enabled: bool
    latest_alarm: str = "無警報"
