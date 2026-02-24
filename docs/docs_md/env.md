# Gestion des secrets avec `.env`

## Objectif
Éviter de stocker des identifiants sensibles (mots de passe, tokens, etc.) dans le code ou les fichiers de configuration versionnés (GitHub).

Les secrets sont chargés via des **variables d’environnement** à partir d’un fichier `.env` local, non commité.

---

## Principe

- Le fichier `.env` contient les secrets (ex. mot de passe BDD)
- Le code Python lit ces valeurs via `os.getenv(...)`
- Le fichier `.env` est **exclu du dépôt Git** (`.gitignore`)
- Un fichier `.env.example` est fourni pour documenter les variables attendues


## Chargement des valeurs

Le fichier .env est chargé au démarrage via python-dotenv :

```python
from dotenv import load_dotenv
load_dotenv()

import os
db_password = os.getenv("DB_PASSWORD")
```

## Exécution avec sudo

Lorsque l’application nécessite sudo (lecture de journald), il faut conserver les variables d’environnement :

```bash
sudo -E .venv/bin/python main.py --follow
```

Sans -E, les variables définies dans .env ne sont pas transmises au processus.


## Bonnes pratiques
- Ne jamais commit un fichier .env
- Utiliser .env.example pour documenter les variables attendues
- Changer les mots de passe s’ils ont été exposés