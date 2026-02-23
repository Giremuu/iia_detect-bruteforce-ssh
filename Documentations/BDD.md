# BDD – MariaDB + phpMyAdmin (Localhost) — Projet Détection Bruteforce SSH

## Objectif
Mettre en place une base de données locale pour stocker :
- les hôtes, utilisateurs SSH, règles de détection
- les alertes générées
- les rapports produits par l’outil (JSON/texte)

Cette BDD sert de support au projet (Merise → MPD → implémentation Python).

---

## Stack
- **MariaDB**
- **phpMyAdmin**

---

## Installation (Debian 13)

```bash
sudo apt update
sudo apt install -y mariadb-server apache2 php libapache2-mod-php php-mysql php-mbstring phpmyadmin
sudo phpenmod mbstring
sudo systemctl restart apache2
sudo systemctl enable --now mariadb
sudo mariadb-secure-installation
```


## Création de la base et de l’utilisateur

```sql
CREATE DATABASE ssh_bruteforce
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'sshmon'@'localhost' IDENTIFIED BY 'CHANGE_ME';
GRANT ALL PRIVILEGES ON ssh_bruteforce.* TO 'sshmon'@'localhost';
FLUSH PRIVILEGES;
```

### L'utilisation de cet utilisateur dédié permet d'éviter d'utiliser root dans le futur code Python (bonne pratique sécurité).

---

## Modèle de données
hote : machine surveillée (MAC, IP, OS)
utilisateur : utilisateur SSH (clé publique)
authentifier : association hôte ↔ utilisateur
regle : règles de détection
alerte : alerte déclenchée (date, hôte, règle)
rapport : données générées pour une alerte

Choix de conception :
- identifiants techniques (id_*) pour simplifier les relations
- stockage des rapports en base pour conserver l’historique
- clés étrangères pour respecter le MCD/MLD