import unittest

from webapp.server import create_app


class FakeRuntime:

    def __init__(self):
        self.started = False

    def start(self):
        self.started = True

    def get_status(self):
        return {
            "fps": 12.3,
            "detections_count": 2,
            "inside_boundary_count": 1,
            "landmarks_count": 0,
            "active_tracks_count": 2,
            "esp32_mode": "mock",
            "stabilization_enabled": False,
            "latest_alarm": "無警報",
            "error": None,
        }

    def get_alarms(self):
        return [
            {
                "time": "12:00:00",
                "message": "警報：human ID 1 進入邊界",
            }
        ]

    def get_frame(self):
        return None

    def get_settings(self):
        return {
            "yolo_device": "cuda",
            "yolo_image_size": 640,
            "yolo_half": False,
            "frame_width": 800,
            "vision_process_interval": 10,
            "runtime_target_fps": 10,
            "web_stream_fps": 10,
            "web_jpeg_quality": 70,
            "video_realtime_playback": True,
            "esp32_enabled": False,
        }

    def get_source(self):
        return {
            "mode": "video",
            "value": "videos/test.mp4",
            "source": "videos/test.mp4",
            "label": "test video",
        }

    def set_source(self, mode, value=None):
        return {
            "mode": mode,
            "value": value,
            "source": value,
            "label": mode,
        }


class WebAppTest(unittest.TestCase):

    def test_status_endpoint(self):
        runtime = FakeRuntime()
        app = create_app(runtime)
        client = app.test_client()

        response = client.get("/api/status")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(runtime.started)
        self.assertEqual(response.get_json()["detections_count"], 2)

    def test_alarms_endpoint(self):
        app = create_app(FakeRuntime())
        client = app.test_client()

        response = client.get("/api/alarms")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["time"], "12:00:00")

    def test_alarms_csv_endpoint(self):
        app = create_app(FakeRuntime())
        client = app.test_client()

        response = client.get("/api/alarms.csv")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn("skyeyes_alarms.csv", response.headers["Content-Disposition"])
        self.assertTrue(response.data.startswith(b"\xef\xbb\xbf"))
        self.assertIn("時間,警報內容", response.data.decode("utf-8-sig"))

    def test_settings_endpoint(self):
        app = create_app(FakeRuntime())
        client = app.test_client()

        response = client.get("/api/settings")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["runtime_target_fps"], 10)

    def test_source_endpoint(self):
        app = create_app(FakeRuntime())
        client = app.test_client()

        response = client.get("/api/source")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["mode"], "video")

    def test_source_update_endpoint(self):
        app = create_app(FakeRuntime())
        client = app.test_client()

        response = client.post(
            "/api/source",
            json={"mode": "webcam", "value": "1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["mode"], "webcam")


if __name__ == "__main__":
    unittest.main()
