# Logique Python & Code

## Objectif
Ce projet Python permet de détecter le bruteforce SSH basé `journald`. Il applique une règle simple pour détecter les échecs d’authentification et garde les alertes dans une BDD MariaDB.

---

## Vue d’ensemble

Le programme :
1. Lit les logs SSH via `journalctl -o json`
2. Parse uniquement les événements d’authentification en échec
3. Agrège les échecs par IP
4. Déclenche une alerte quand un seuil est atteint (Règle dans main.py)
5. Stocke l’alerte et un rapport JSON en base de données

---

## main.py

Rôle :
- Lit les arguments CLI (`--config`, `--follow`, `--once`)
- Charge la configuration (.env, config.yaml...)
- Initialise la règle de détection
- Ouvre la connexion DB via un wrapper
- Boucle sur les logs journald
- Persiste les alertes

---

## config.py

Objectif :
- Charger `config.yaml`
- Charger `.env` pour les secrets
- Supporter `${VAR}` dans le YAML
- Convertir la config en objets typés

Concepts :
- `JournaldCfg` : service systemd + follow
- `DetectionCfg` : seuil + fenêtre temporelle
- `DbCfg` : paramètres DB (sans mot de passe)
- `HostCfg` : infos de l’hôte
- `AppCfg` : agrégat global

Avantages :
- Configuration typée
- Valeurs par défaut
- Séparation secrets / config

---

## journald_reader.py

Objectif :
- Lancer `journalctl` en sous-processus
- Lire les logs en JSON ligne par ligne
- Fournir un itérateur Python

---

## parser.py 

Objectif :
- Extraire uniquement les échecs SSH utiles
- Transformer une entrée brute journald en `AuthEvent`

Éléments clés :
- Regex sur messages SSH (`Failed password`, `Invalid user`)
- Extraction de :
  - IP source
  - utilisateur
  - timestamp
- Normalisation dans un objet immuable `AuthEvent`

---

## detector.py – Détection par fenêtre glissante

Objectif :
- Détecter un bruteforce SSH via une règle simple :
  > N échecs depuis la même IP en X secondes

Structure :
- `RuleConfig` :
  - `threshold`
  - `window_seconds`

- `SlidingWindowDetector` :
  - Maintient un dictionnaire
  - Nettoie les événements hors fenêtre
  - Déclenche une alerte quand `len(queue) == threshold`

Sortie :
- Dictionnaire prêt à être persisté en base :
  - IP
  - compteur
  - date de déclenchement
  - rapport JSON

---

## db.py

Objectif :
- Encapsuler PyMySQL dans une API simple
- Gérer automatiquement la connexion via `with db:`
- Fonctions métier :
  - `ensure_host()` : garantit l’existence de l’hôte
  - `get_or_create_rule()` : garantit l’existence de la règle
  - `insert_alert()` : insère une alerte
  - `insert_report()` : insère un rapport lié

Avantages :
- Centralisation de l’accès DB
- Moins de duplication de code

---

## Principes de conception

- **Séparation des responsabilités**
  - Lecture logs / parsing / détection / persistance sont découplés
- **Flux orienté événements**
  - Chaque log est transformé en événement métier (`AuthEvent`)
- **Détection temps réel**
  - Traitement ligne par ligne (streaming)
- **Configuration externe**
  - YAML + `.env`
- **Sécurité minimale**
  - Secrets hors du dépôt (variables d’environnement)

---

## Évolutions possibles

- Ajouter la détection des succès (corrélation FAIL → SUCCESS)
- Ajouter d’autres règles (ex : multi-IP, seuil global)
- Ajout de backend de notification (mail, webhook, SIEM)
- Ajout de métriques / Supervision (Prometheus)