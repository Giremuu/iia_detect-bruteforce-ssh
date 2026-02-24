import pytest
from datetime import datetime, timedelta, timezone

from ssh_detector.detector import RuleConfig, SlidingWindowDetector
from ssh_detector.parser import AuthEvent


def _ev(ts, ip="1.2.3.4", user="u", outcome="FAIL", msg=""):
    return AuthEvent(ts=ts, ip=ip, username=user, outcome=outcome, message=msg)


def test_success_does_not_count_toward_threshold():
    """
    Seuls les FAIL comptent.
    """
    rule = RuleConfig(threshold=5, window_seconds=120)
    det = SlidingWindowDetector(rule)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # 4 FAIL + 1 SUCCESS => pas d'alerte
    for i in range(4):
        assert det.feed(_ev(base + timedelta(seconds=i * 5), outcome="FAIL")) is None

    assert det.feed(_ev(base + timedelta(seconds=25), outcome="SUCCESS")) is None

    # 5e FAIL => alerte
    alert = det.feed(_ev(base + timedelta(seconds=30), outcome="FAIL"))
    assert alert is not None
    assert alert["count"] == 5


def test_threshold_one_alerts_immediately():
    """
    Cas limite : threshold=1 => un seul FAIL doit déclencher.
    """
    rule = RuleConfig(threshold=1, window_seconds=120)
    det = SlidingWindowDetector(rule)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    alert = det.feed(_ev(base, ip="8.8.8.8"))
    assert alert is not None
    assert alert["ip"] == "8.8.8.8"
    assert alert["count"] == 1


def test_events_from_different_users_same_ip():
    """
    La règle est par IP uniquement, des usernames différents doivent quand même compter.
    """
    rule = RuleConfig(threshold=3, window_seconds=60)
    det = SlidingWindowDetector(rule)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert det.feed(_ev(base, ip="9.9.9.9", user="u1")) is None
    assert det.feed(_ev(base + timedelta(seconds=5), ip="9.9.9.9", user="u2")) is None
    alert = det.feed(_ev(base + timedelta(seconds=10), ip="9.9.9.9", user="u3"))
    assert alert is not None
    assert alert["ip"] == "9.9.9.9"
    assert alert["count"] == 3


def test_non_fail_outcomes_do_not_crash_and_do_not_alert():
    """
    Outcomes inattendus ne doivent pas faire planter le détecteur
    et ne doivent pas déclencher d'alerte normalement
    """
    rule = RuleConfig(threshold=2, window_seconds=60)
    det = SlidingWindowDetector(rule)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert det.feed(_ev(base, outcome="INFO")) is None
    assert det.feed(_ev(base + timedelta(seconds=1), outcome="INVALID")) is None
    assert det.feed(_ev(base + timedelta(seconds=2), outcome="SUCCESS")) is None

    # Le premier FAIL seul ne suffit pas à alerter (threshold=2)
    assert det.feed(_ev(base + timedelta(seconds=3), outcome="FAIL")) is None


@pytest.mark.xfail(
    reason="Certains systèmes émettent une alerte à chaque nouvel événement au-dessus du seuil."
)
def test_alert_only_on_crossing_threshold_optional():
    """
    Contrat possible : alerte uniquement au moment où on atteint le seuil,
    pas pour chaque FAIL supplémentaire tant que la fenêtre reste au-dessus.
    """
    rule = RuleConfig(threshold=3, window_seconds=120)
    det = SlidingWindowDetector(rule)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert det.feed(_ev(base, ip="7.7.7.7")) is None
    assert det.feed(_ev(base + timedelta(seconds=1), ip="7.7.7.7")) is None

    alert = det.feed(_ev(base + timedelta(seconds=2), ip="7.7.7.7"))
    assert alert is not None

    # FAIL supplémentaire => pas de nouvelle alerte (selon ce contrat)
    assert det.feed(_ev(base + timedelta(seconds=3), ip="7.7.7.7")) is None
