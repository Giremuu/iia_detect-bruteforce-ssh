# CI/CD (GitHub Actions) — Ruff + PyTest

## Objectif
Mettre en place une CI simple qui s’exécute à chaque `push` / `pull_request` pour :
- vérifier la qualité du code (lint + format)
- exécuter les tests unitaires

---

## Outils utilisés

### Ruff
Ruff est un outil rapide qui regroupe :
- **lint** : détecte erreurs et mauvaises pratiques (imports inutiles, variables non utilisées, etc.)
- **format** : applique un formatage automatique

Commandes utilisées :
- `ruff check .` : lint
- `ruff format .` : formate
- `ruff format --check .` : vérifie le format sans modifier

### PyTest
PyTest exécute les tests unitaires contenus dans `tests/` :
- `pytest -q` : lance les tests en mode compact

---

## Dépendances

### requirements-dev.txt
Les outils de dev/CI sont installés via `requirements-dev.txt`


## Configuration PyTest

Pour permettre aux tests d’importer src.*, on ajoute pytest.ini à la racine :
```python
[pytest]
pythonpath = .
testpaths = tests
```

## Github Action :

Le workflow :
- tourne sur Ubuntu (runner GitHub)
- teste plusieurs versions de Python (matrice)
- installe les dépendances
- lance Ruff + PyTest
- lance pip-audit sans bloquer