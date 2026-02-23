"""
Lance journalctl en sous-processus, lit ses sorties en continu ou en one-shot, convertit chaque ligne
en dictionnaire Python et les fournit au reste du programme
"""

import json
import subprocess
from typing import Dict, Iterator, Any


def iter_journald_json(
    unit: str = "ssh", follow: bool = True
) -> Iterator[Dict[str, Any]]:
    # Construction de la commande pour journalctl
    cmd = ["journalctl", "-u", unit, "-o", "json"]
    if follow:
        cmd.insert(1, "-f")

    # Lancement du process
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Décodage JSON + yield
    assert p.stdout is not None
    for line in p.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue
