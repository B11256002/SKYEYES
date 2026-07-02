from core.esp32 import ESP32Status


class MockESP32Communicator:

    def __init__(self):
        self.sent_commands = []
        self.status = ESP32Status(
            connected=False,
            mode="mock",
            message="ESP32 mock mode"
        )

    def connect(self):
        return self.status

    def send(self, command):
        self.sent_commands.append(command)
        return True

    def read_status(self):
        return self.status

    def close(self):
        return None
