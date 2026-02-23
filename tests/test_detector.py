from datetime import datetime, timedelta, timezone

from src.detector import RuleConfig, SlidingWindowDetector
from src.parser import AuthEvent


def test_alert_on_threshold():
    rule = RuleConfig(threshold=5, window_seconds=120)
    det = SlidingWindowDetector(rule)

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    alert = None
    for i in range(5):
        ev = AuthEvent(
            ts=base + timedelta(seconds=i * 10),
            ip="::1",
            username="fakeuser",
            outcome="FAIL",
            message="Failed password for fakeuser from ::1",
        )
        alert = det.feed(ev)

    assert alert is not None
    assert alert["ip"] == "::1"
    assert alert["count"] == 5


def test_window_expires_old_events():
    rule = RuleConfig(threshold=3, window_seconds=30)
    det = SlidingWindowDetector(rule)

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert det.feed(AuthEvent(base, "1.2.3.4", "u", "FAIL", "")) is None
    assert det.feed(AuthEvent(base + timedelta(seconds=5), "1.2.3.4", "u", "FAIL", "")) is None

    # event outside window -> should not reach threshold
    assert det.feed(AuthEvent(base + timedelta(seconds=40), "1.2.3.4", "u", "FAIL", "")) is None