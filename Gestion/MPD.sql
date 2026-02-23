-- MPD MariaDB (compatible phpMyAdmin)
-- Engine: InnoDB (FK OK) / Charset: utf8mb4

CREATE DATABASE IF NOT EXISTS ssh_bruteforce
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE ssh_bruteforce;

-- =========================
-- 1) Tables
-- =========================

CREATE TABLE hote (
  id_hote      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  adresse_mac  VARCHAR(17)     NOT NULL,  -- aa:bb:cc:dd:ee:ff
  adresse_ip   VARCHAR(45)     NOT NULL,  -- IPv4/IPv6
  os           VARCHAR(80)     NOT NULL,
  PRIMARY KEY (id_hote),
  UNIQUE KEY uq_hote_mac (adresse_mac),
  UNIQUE KEY uq_hote_ip  (adresse_ip)
) ENGINE=InnoDB;

CREATE TABLE utilisateur (
  id_user      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  ssh_clee_pub VARCHAR(255)    NOT NULL,
  PRIMARY KEY (id_user)
) ENGINE=InnoDB;

CREATE TABLE regle (
  id_regle   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `condition` VARCHAR(255)   NOT NULL,

  PRIMARY KEY (id_regle)
) ENGINE=InnoDB;

CREATE TABLE rapport (
  id_rapport BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  format     VARCHAR(255)    NOT NULL,   -- console/json/...
  donnee     LONGTEXT        NOT NULL,   -- JSON stocké (MariaDB)

  PRIMARY KEY (id_rapport)
) ENGINE=InnoDB;

-- =========================
-- 2) Associations
-- =========================

CREATE TABLE authentifier (
  id_hote      BIGINT UNSIGNED NOT NULL,
  id_user      BIGINT UNSIGNED NOT NULL,
  autorisation TINYINT(1)      NOT NULL DEFAULT 1,

  PRIMARY KEY (id_hote, id_user),

  CONSTRAINT fk_auth_hote FOREIGN KEY (id_hote)
    REFERENCES hote(id_hote)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_auth_user FOREIGN KEY (id_user)
    REFERENCES utilisateur(id_user)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================
-- 3) ALERTE (FK vers HOTE, REGLE, RAPPORT)
--    + date de déclenchement (attribut de l'asso "Déclencher")
-- =========================

CREATE TABLE alerte (
  id_alerte           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  id_hote             BIGINT UNSIGNED NOT NULL,
  id_regle            BIGINT UNSIGNED NOT NULL,
  id_rapport          BIGINT UNSIGNED NOT NULL,
  date_declenchement  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_alerte),
  KEY idx_alerte_hote    (id_hote),
  KEY idx_alerte_regle   (id_regle),
  KEY idx_alerte_rapport (id_rapport),
  KEY idx_alerte_date    (date_declenchement),

  CONSTRAINT fk_alerte_hote FOREIGN KEY (id_hote)
    REFERENCES hote(id_hote)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT fk_alerte_regle FOREIGN KEY (id_regle)
    REFERENCES regle(id_regle)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT fk_alerte_rapport FOREIGN KEY (id_rapport)
    REFERENCES rapport(id_rapport)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;