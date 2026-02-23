"""
Module qui transforme une entrée brute de journald en un objet AuthEvent uniquement quand c'est un échec d’auth SSH,
en extrayant l’IP, l’utilisateur et le timestamp
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import re

FAIL_PATTERNS = [
    re.compile(r"Failed password for (invalid user )?(?P<user>\S+) from (?P<ip>\S+)"),
    re.compile(r"Invalid user (?P<user>\S+) from (?P<ip>\S+)"),
]

@dataclass(frozen=True)
# Structure de l'objet AuthEvent
class AuthEvent:
    ts: datetime
    ip: str
    username: str
    outcome: str
    message: str

def _journald_ts(entry: Dict[str, Any]) -> datetime:
    # Conversion du timestamp journald en DATETIME pour Python
    rt = entry.get("__REALTIME_TIMESTAMP")
    if rt is None:
        return datetime.now(timezone.utc)
    try:
        us = int(rt)
        return datetime.fromtimestamp(us / 1_000_000, tz=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def parse_auth_event(entry: Dict[str, Any]) -> Optional[AuthEvent]:
    # Parsing d’une entrée de log journald
    msg = entry.get("MESSAGE")
    if not isinstance(msg, str):
        return None

    # Détection des échecs SSH via regex
    for pat in FAIL_PATTERNS:
        m = pat.search(msg)
        if m:
            ts = _journald_ts(entry)
            user = m.group("user")
            ip = m.group("ip")
            return AuthEvent(ts=ts, ip=ip, username=user, outcome="FAIL", message=msg)

    return None