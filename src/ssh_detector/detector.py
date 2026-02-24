"""
Maintient, pour chaque IP, une liste des échecs récents dans une fenêtre
temporelle glissante et déclenche une alerte en fonction de la règle
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from collections import deque
from typing import Deque, Dict, Optional, Any
import json


@dataclass(frozen=True)
class RuleConfig:
    threshold: int
    window_seconds: int


class SlidingWindowDetector:
    """
    Tracks FAIL events per IP in a sliding time window.
    Emits an alert when threshold is reached.
    """

    def __init__(self, cfg: RuleConfig) -> None:
        self.cfg = cfg
        self.failures: Dict[str, Deque[datetime]] = {}

    def feed(self, ev) -> Optional[Dict[str, Any]]:
        if ev.outcome != "FAIL":
            return None

        now = ev.ts if ev.ts.tzinfo else ev.ts.replace(tzinfo=timezone.utc)
        window_start = now - timedelta(seconds=self.cfg.window_seconds)

        q = self.failures.setdefault(ev.ip, deque())
        q.append(now)

        while q and q[0] < window_start:
            q.popleft()

        # Construction du rapport d’alerte
        if len(q) >= self.cfg.threshold:
            payload = {
                "type": "BRUTEFORCE_SSH_DETECTED",
                "ip": ev.ip,
                "count": len(q),
                "window_seconds": self.cfg.window_seconds,
                "date_declenchement": now.isoformat(),
                "sample_message": ev.message,
            }
            return {
                "ip": ev.ip,
                "count": len(q),
                "date_declenchement": now.replace(tzinfo=None),  # DB DATETIME
                "report_json": json.dumps(payload, ensure_ascii=False),
            }

        return None
