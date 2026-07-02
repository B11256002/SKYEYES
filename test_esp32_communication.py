import unittest

from communication.factory import create_esp32_communicator
from communication.mock import MockESP32Communicator
from communication.protocol import decode_status, encode_command, make_command


class ESP32CommunicationTest(unittest.TestCase):

    def test_encodes_command_as_json_line(self):
        command = make_command("ALARM", "person entered boundary")

        encoded = encode_command(command)

        self.assertEqual(
            encoded,
            '{"command":"ALARM","value":"person entered boundary"}\n'
        )

    def test_decodes_status_from_json_line(self):
        status = decode_status(
            '{"connected":true,"mode":"serial","message":"ready"}'
        )

        self.assertTrue(status.connected)
        self.assertEqual(status.mode, "serial")
        self.assertEqual(status.message, "ready")

    def test_mock_records_sent_commands(self):
        communicator = MockESP32Communicator()
        command = make_command("PING")

        communicator.connect()
        sent = communicator.send(command)

        self.assertTrue(sent)
        self.assertEqual(communicator.sent_commands, [command])

    def test_factory_uses_mock_when_disabled(self):
        communicator = create_esp32_communicator(
            enabled=False,
            port="COM3",
            baudrate=115200
        )

        self.assertIsInstance(communicator, MockESP32Communicator)


if __name__ == "__main__":
    unittest.main()
