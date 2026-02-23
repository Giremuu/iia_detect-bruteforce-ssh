"""
Feb 2026 - Gwilherm LE GALLIC

Programme principal qui :
- lit les logs d’authentification (via journald)
- détecte un bruteforce SSH
- enregistre l’alerte dans une base de données
- affiche un message d’alerte à l’écran.
"""

# 1) Imports des fonctions construites dans src/
import argparse
import os

from src.config import load_config
from src.journald_reader import iter_journald_json
from src.parser import parse_auth_event
from src.detector import SlidingWindowDetector, RuleConfig
from src.db import Database, ensure_host, get_or_create_rule, insert_alert, insert_report


def main() -> int:
# Lecture des options de la CLI
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")                                          # Permet de spécifier un chemin vers le conf.yaml
    ap.add_argument("--follow", action="store_true", help="follow journald")                    # Permet de lancer en continue (pour tests)
    ap.add_argument("--once", action="store_true", help="read current logs then exit")          # Permet de lire une fois les logs et reporter l'info (pour crontab)
    args = ap.parse_args()

    cfg = load_config(args.config)

    follow = bool(args.follow) or cfg.journald.follow
    if args.once:
        follow = False

    # Règles de détection
    rule = RuleConfig(
        threshold=int(cfg.detection.threshold),
        window_seconds=int(cfg.detection.window_seconds),
    )
    detector = SlidingWindowDetector(rule)

    # Récupération des creds du .env pour accéder à la DB
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise SystemExit("DB_PASSWORD is not set. Use a .env file or export DB_PASSWORD.")

    db = Database(
        host=cfg.db.host,
        user=cfg.db.user,
        password=db_password,
        database=cfg.db.database,
    )

    # Enregistre dans la DB
    with db:
        id_hote = ensure_host(
            db,
            adresse_mac=cfg.host.adresse_mac,
            adresse_ip=cfg.host.adresse_ip,
            os_name=cfg.host.os,
        )
        id_regle = get_or_create_rule(
            db,
            conditions=f"{rule.threshold} FAIL in {rule.window_seconds}s from same IP",
        )

        # Boucle : lecture des logs > parsing > détection
        for entry in iter_journald_json(unit=cfg.journald.unit, follow=follow):
            ev = parse_auth_event(entry)
            if ev is None:
                continue

            alert = detector.feed(ev)
            if alert is None:
                continue

            # Si alerte : insertion en DB
            id_alerte = insert_alert(
                db,
                id_hote=id_hote,
                id_regle=id_regle,
                date_declenchement=alert["date_declenchement"],
            )
            insert_report(
                db,
                id_alerte=id_alerte,
                fmt="json",
                donnees=alert["report_json"],
            )

            print(f"[ALERTE] Bruteforce suspect IP={alert['ip']} count={alert['count']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())