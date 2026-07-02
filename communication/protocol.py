import json

from core.esp32 import ESP32Command, ESP32Status


def encode_command(command):
    payload = {
        "command": command.name,
        "value": command.value,
    }

    return json.dumps(payload, separators=(",", ":")) + "\n"


def decode_status(line):
    payload = json.loads(line)

    return ESP32Status(
        connected=bool(payload.get("connected", True)),
        mode=str(payload.get("mode", "unknown")),
        message=str(payload.get("message", ""))
    )


def make_command(name, value=""):
    return ESP32Command(name=name, value=value)
