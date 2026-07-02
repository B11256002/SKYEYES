import unittest

import numpy as np

from core.system_status import SystemStatus
from ui.display import Display


class DisplayDashboardTest(unittest.TestCase):

    def test_dashboard_extends_frame_width(self):
        display = Display("test")
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        status = SystemStatus(
            fps=30.0,
            detections_count=2,
            inside_boundary_count=1,
            landmarks_count=1,
            active_tracks_count=2,
            esp32_mode="mock",
            stabilization_enabled=True,
            latest_alarm="警報：person ID 1 進入邊界"
        )

        output = display.draw_dashboard(frame, status)

        self.assertEqual(output.shape[0], 240)
        self.assertEqual(output.shape[1], 320 + display.panel_width)


if __name__ == "__main__":
    unittest.main()
