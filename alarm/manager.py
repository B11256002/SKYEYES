import time

from core.alarm import AlarmEvent


class AlarmManager:

    def __init__(self, cooldown_seconds=2.0, clock=None):
        self.cooldown_seconds = cooldown_seconds
        self.clock = clock or time.time
        self.last_alarm_time = {}
        self.latest_event = None

    def update(self, detections):
        events = []

        for detection in detections:
            if not detection.inside_boundary:
                continue

            event_key = self._event_key(detection)
            now = self.clock()
            last_time = self.last_alarm_time.get(event_key)

            if last_time is not None and now - last_time < self.cooldown_seconds:
                continue

            self.last_alarm_time[event_key] = now
            event = self._create_event(detection, now)
            self.latest_event = event
            events.append(event)

        return events

    def _event_key(self, detection):
        if detection.tracked_id != -1:
            return f"id:{detection.tracked_id}"

        return f"{detection.label}:{detection.center}"

    def _create_event(self, detection, timestamp):
        track_label = ""

        if detection.tracked_id != -1:
            track_label = f" ID {detection.tracked_id}"

        message = (
            f"ALARM {detection.label}{track_label} entered boundary "
            f"at {detection.center} ({detection.confidence:.2f})"
        )

        return AlarmEvent(
            label=detection.label,
            confidence=detection.confidence,
            center=detection.center,
            timestamp=timestamp,
            message=message
        )
