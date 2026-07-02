from dataclasses import dataclass


@dataclass
class ESP32Command:

    name: str
    value: str = ""


@dataclass
class ESP32Status:

    connected: bool
    mode: str = "offline"
    message: str = ""
