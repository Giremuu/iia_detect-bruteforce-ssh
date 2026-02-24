# Détecteur de Bruteforce SSH (Blue Team)

## Présentation

Ce projet est un outil de détection de tentatives de bruteforce SSH à partir des journaux système `journald` sous Debian 13.  
Il analyse les échecs d’authentification SSH sur une fenêtre temporelle glissante et génère des alertes lorsqu’un comportement suspect est identifié.

**Objectifs pédagogiques :**
- Exploiter les logs système pour la détection d’incidents de sécurité  
- Mettre en œuvre une logique de détection par règles  
- Appliquer des méthodes de modélisation (Merise) et de conception objet (UML) dans le cadre du cours *Gestion des SI*

---

## Fonctionnalités

- Collecte des logs SSH via `journalctl`  
- Parsing des événements d’authentification (succès / échecs)  
- Détection de bruteforce basée sur des seuils configurables  
- Génération et stockage d’alertes en base de données  

---

## Environnement et prérequis

- **OS** : Debian 13  
- **Service** : `openssh-server` actif  
- **Accès logs** : droits `sudo` pour la lecture de `journald`  
- **Langage** : Python 3  
- **Base de données** : MariaDB / MySQL (accès via utilisateur dédié)

---

## Sources de logs

Le projet s’appuie sur `journald` (par défaut sous Debian 13) :

- Consultation des logs SSH :  
```bash
sudo journalctl -u ssh
sudo journalctl -f -u ssh
sudo journalctl -u ssh -o json
```

---

## Règle de détection
Condition :
- 5 tentatives d’authentification échouées depuis la même adresse IP en moins de 2 minutes

Action :
- Génération d’une alerte de type BRUTEFORCE_SSH_DETECTED
- Enregistrement de l’alerte en base de données

---

## Procédure de test
Si vous avez cloné ce repo :
- modifié et renommé le .env en fonction de votre environnement
- modifié et renommé le config.yaml en fonction de votre environnement
- Lancer le détecteur en mode infini :
```bash
sudo -E .venv/bin/python main.py --follow
```
- Générer des échecs d’authentification SSH depuis la même machine ou une autre :
```bash
ssh fakeuser@localhost
```

Vérifier :
- Les événements sont visibles dans journalctl
- Une alerte est générée après dépassement du seuil
- L’alerte est enregistrée en base de données

---

## Modélisation

La modélisation des données suit la méthode Merise avec les entités principales suivantes :
- Événement
- Adresse IP
- Règle
- Alerte
- Hôte

Livrables :
Dans le dossier "GestionSI"
- MCD (Modèle Conceptuel de Données)
- MLD (Modèle Logique de Données)
- MPD (Modèle Physique de Données)

---

## Stack / Outils (AGL) :
- GitHub : gestion de version et CI/CD avec Github Action
- VS Code : édition du code
- Draw.io : schémas et modélisation
- Python : langage principal
- PyTest : framework de tests du code
- Ruff : linting et formatage du code
- Doxyfile : documentations (```doxygen Doxyfile``` - placé en gitignore pour ne pas surchargé le repo)