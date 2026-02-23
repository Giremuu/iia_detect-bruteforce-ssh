"""
charge la configuration depuis un fichier YAML et un .env, remplace les références à des variables d’environnement
pour les secrets, puis transforme le tout en objets typés faciles à utiliser
"""

from dataclasses import dataclass
import os
import yaml
from dotenv import load_dotenv

# Variables d'env
def _expand_env(value: str) -> str:
    # support "${VAR}"
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        var = value[2:-1]
        return os.getenv(var, "")
    return value

# Dataclasses de configuration :
@dataclass
class JournaldCfg:
    unit: str = "ssh"
    follow: bool = True

@dataclass
class DetectionCfg:
    threshold: int = 5
    window_seconds: int = 120

@dataclass
class DbCfg:
    host: str = "127.0.0.1"
    user: str = "sshmon"
    database: str = "ssh_bruteforce"

@dataclass
class HostCfg:
    adresse_mac: str = "00:00:00:00:00:00"
    adresse_ip: str = "127.0.0.1"
    os: str = "Debian"

@dataclass
class AppCfg:
    journald: JournaldCfg
    detection: DetectionCfg
    db: DbCfg
    host: HostCfg

# Chargement du .env
def load_config(path: str) -> AppCfg:
    load_dotenv()  # charge .env si présent (local)

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    journald = raw.get("journald", {})
    detection = raw.get("detection", {})
    db = raw.get("db", {})
    host = raw.get("host", {})

    # expansion ${VAR}
    db = {k: _expand_env(v) for k, v in db.items()}

    return AppCfg(
        journald=JournaldCfg(**journald),
        detection=DetectionCfg(**detection),
        db=DbCfg(**db),
        host=HostCfg(**host),
    )