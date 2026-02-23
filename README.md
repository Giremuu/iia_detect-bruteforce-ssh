# Détecteur de Bruteforce SSH (Blue Team)


## Présentation

Ce projet est un outil permettant de détecter des tentatives de bruteforce SSH à partir des journaux système (journald) sous Debian 13.
Il analyse les échecs d’authentification SSH sur une fenêtre temporelle et génère des alertes lorsqu’un comportement suspect est détecté.

Objectifs pédagogiques :
- Comprendre l’exploitation des logs système pour la détection d’incidents de sécurité
- Mettre en œuvre une logique de détection par règles
- Modéliser les données (Merise) et la conception objet (UML) en suivant les principes du cours Gestion SI


## Fonctionnalités

Collecte des logs SSH via journalctl
Parsing des événements d’authentification (succès/échecs)
Détection de bruteforce basée sur seuils (X échecs en Y minutes)
Génération d’alertes


## Environnement et prérequis

OS : Debian 13
Service SSH actif (openssh-server)
Accès aux logs systemd (droits sudo pour lecture journald)
Langage : Python


## Sources de logs

Le projet utilise journald (par défaut sur Debian 13) :
- sudo journalctl -u ssh

Mode temps réel :
- sudo journalctl -f -u ssh

Export en JSON :
- sudo journalctl -u ssh -o json


## Règle de détection

Condition :
- 5 tentatives d’authentification échouées depuis la même adresse IP en moins de 2 minutes

Action :
- Génération d’une alerte de type BRUTEFORCE_SSH_DETECTED


## Procédure de test

Lancer le détecteur en mode suivi :
- sudo python3 main.py --follow

Générer des échecs SSH depuis le même PC :
- ssh fakeuser@localhost

Vérifier :
- Les événements apparaissent via journalctl
- Une alerte est générée après dépassement du seuil et sera dans la BDD


## Modélisation

Merise décrivant les entités principales (Événement, Adresse IP, Règle, Alerte, Hôte) :
- MCD
- MLD
- MPD


## Stacks / Outils AGL :
- Github avec CI/CD pour tests de lint ect
- VScode pour l'écriture du code
- DrawIO pour les schémas et modèles
- Python comme language de programmation
- PyTest pour les tests de l'outil


## Steps :
- [x] MCD
- [x] MLD
- [x] MPD
- [x] Base de données (PHPMyAdmin et BDD en local)
- [x] Création de l'utilisateur userssh pour gérer la BDD
- [X] Code Python
- [ ] Github CI/CD
- [ ] PyTest