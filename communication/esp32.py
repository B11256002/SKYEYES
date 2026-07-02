from communication.protocol import decode_status, encode_command
from core.esp32 import ESP32Status


class ESP32Communicator:

    def __init__(self, port, baudrate=115200, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        try:
            import serial

            self.serial = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )
        except ImportError as exc:
            raise RuntimeError(
                "pyserial is required for ESP32 serial communication."
            ) from exc

        return ESP32Status(
            connected=True,
            mode="serial",
            message=f"Connected to {self.port}"
        )

    def send(self, command):
        if self.serial is None:
            return False

        encoded = encode_command(command).encode("utf-8")
        self.serial.write(encoded)
        return True

    def read_status(self):
        if self.serial is None:
            return ESP32Status(
                connected=False,
                mode="serial",
                message="Serial port is not connected"
            )

        line = self.serial.readline().decode("utf-8").strip()

        if not line:
            return ESP32Status(
                connected=True,
                mode="serial",
                message="No status received"
            )

        return decode_status(line)

    def close(self):
        if self.serial is not None:
            self.serial.close()
            self.serial = None
