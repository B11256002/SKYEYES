from communication.esp32 import ESP32Communicator
from communication.mock import MockESP32Communicator


def create_esp32_communicator(enabled, port, baudrate):
    if not enabled:
        return MockESP32Communicator()

    return ESP32Communicator(port=port, baudrate=baudrate)
