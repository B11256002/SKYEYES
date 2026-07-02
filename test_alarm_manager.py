import unittest

from alarm.manager import AlarmManager
from core.detection import Detection


class FakeClock:

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class AlarmManagerTest(unittest.TestCase):

    def test_triggers_alarm_for_inside_detection(self):
        clock = FakeClock(100.0)
        alarm = AlarmManager(cooldown_seconds=2.0, clock=clock)
        detection = self._detection(inside_boundary=True)

        events = alarm.update([detection])

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].label, "person")
        self.assertEqual(events[0].center, (50, 50))
        self.assertIs(alarm.latest_event, events[0])

    def test_ignores_outside_detection(self):
        clock = FakeClock(100.0)
        alarm = AlarmManager(cooldown_seconds=2.0, clock=clock)
        detection = self._detection(inside_boundary=False)

        events = alarm.update([detection])

        self.assertEqual(events, [])
        self.assertIsNone(alarm.latest_event)

    def test_respects_cooldown(self):
        clock = FakeClock(100.0)
        alarm = AlarmManager(cooldown_seconds=2.0, clock=clock)
        detection = self._detection(inside_boundary=True)

        first_events = alarm.update([detection])
        clock.value = 101.0
        second_events = alarm.update([detection])
        clock.value = 102.1
        third_events = alarm.update([detection])

        self.assertEqual(len(first_events), 1)
        self.assertEqual(second_events, [])
        self.assertEqual(len(third_events), 1)

    def test_alarm_message_includes_tracked_id(self):
        clock = FakeClock(100.0)
        alarm = AlarmManager(cooldown_seconds=2.0, clock=clock)
        detection = self._detection(inside_boundary=True)
        detection.tracked_id = 3

        events = alarm.update([detection])

        self.assertIn("ID 3", events[0].message)

    def _detection(self, inside_boundary):
        return Detection(
            label="person",
            confidence=0.9,
            corners=[(0, 0), (100, 0), (100, 100), (0, 100)],
            center=(50, 50),
            timestamp=100.0,
            inside_boundary=inside_boundary
        )


if __name__ == "__main__":
    unittest.main()
