"""
Ce fichier fournit des fonctions utilitaires pour l’existence des hôtes, règles ect..
puis enregistrer une alerte et son rapport dans une BDD
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import pymysql

# Wrapper simple autour de PyMySQL
@dataclass
class Database:
    host: str
    user: str
    password: str
    database: str
    conn: Optional[pymysql.connections.Connection] = None

    # Ouvre la connexion à la BDD
    def __enter__(self) -> "Database":
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        return self

    # Fermeture de la connexion à la BDD
    def __exit__(self, exc_type, exc, tb) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    # Exécute une requête SQL
    def execute(self, sql: str, params=None):
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return cur

# Récupère ou créer l’hôte
def ensure_host(db: Database, adresse_mac: str, adresse_ip: str, os_name: str) -> int:
    cur = db.execute("SELECT id_hote FROM hote WHERE adresse_mac=%s", (adresse_mac,))
    row = cur.fetchone()
    if row:
        db.execute("UPDATE hote SET adresse_ip=%s, os=%s WHERE id_hote=%s", (adresse_ip, os_name, row["id_hote"]))
        return int(row["id_hote"])

    cur = db.execute(
        "INSERT INTO hote (adresse_mac, adresse_ip, os) VALUES (%s,%s,%s)",
        (adresse_mac, adresse_ip, os_name),
    )
    return int(cur.lastrowid)

# Récupère ou créer une règle
def get_or_create_rule(db: Database, conditions: str) -> int:
    cur = db.execute("SELECT id_regle FROM regle WHERE conditions=%s", (conditions,))
    row = cur.fetchone()
    if row:
        return int(row["id_regle"])

    cur = db.execute("INSERT INTO regle (conditions) VALUES (%s)", (conditions,))
    return int(cur.lastrowid)

# Créer une alerte
def insert_alert(db: Database, id_hote: int, id_regle: int, date_declenchement: datetime) -> int:
    cur = db.execute(
        "INSERT INTO alerte (id_hote, id_regle, date_declenchement) VALUES (%s,%s,%s)",
        (id_hote, id_regle, date_declenchement),
    )
    return int(cur.lastrowid)

# Créer un rapport
def insert_report(db: Database, id_alerte: int, fmt: str, donnees: str) -> int:
    cur = db.execute(
        "INSERT INTO rapport (id_alerte, format, donnees) VALUES (%s,%s,%s)",
        (id_alerte, fmt, donnees),
    )
    return int(cur.lastrowid)