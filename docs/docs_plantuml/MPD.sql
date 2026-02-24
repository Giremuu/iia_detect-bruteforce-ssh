CREATE DATABASE IF NOT EXISTS ssh_bruteforce
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ssh_bruteforce;

-- =========================
-- TABLE : HOTE
-- =========================
CREATE TABLE hote (
  id_hote BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  adresse_mac VARCHAR(17) NOT NULL,
  adresse_ip  VARCHAR(45) NOT NULL,
  os          VARCHAR(80) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_hote_mac (adresse_mac),
  KEY idx_hote_ip (adresse_ip)
) ENGINE=InnoDB;

-- =========================
-- TABLE : UTILISATEUR
-- =========================
CREATE TABLE utilisateur (
  id_user BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  ssh_clee_pub VARCHAR(255) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_user_pubkey (ssh_clee_pub)
) ENGINE=InnoDB;

-- =========================
-- ASSOCIATION : S'AUTHENTIFIER (M:N) + Autorisation
-- =========================
CREATE TABLE authentifier (
  id_hote BIGINT UNSIGNED NOT NULL,
  id_user BIGINT UNSIGNED NOT NULL,
  autorisation TINYINT(1) NOT NULL DEFAULT 1, -- 1=autorisé, 0=non
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id_hote, id_user),

  CONSTRAINT fk_auth_hote
    FOREIGN KEY (id_hote) REFERENCES hote(id_hote)
    ON DELETE CASCADE ON UPDATE CASCADE,

  CONSTRAINT fk_auth_user
    FOREIGN KEY (id_user) REFERENCES utilisateur(id_user)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================
-- TABLE : REGLE
-- =========================
CREATE TABLE regle (
  id_regle BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  conditions VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================
-- TABLE : ALERTE
-- (Concerne 1 hote) + (Déclenchée par 1 règle) + Date de déclenchement
-- =========================
CREATE TABLE alerte (
  id_alerte BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  id_hote BIGINT UNSIGNED NOT NULL,
  id_regle BIGINT UNSIGNED NOT NULL,
  date_declenchement DATETIME NOT NULL,

  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_alerte_date (date_declenchement),
  KEY idx_alerte_hote (id_hote),
  KEY idx_alerte_regle (id_regle),

  CONSTRAINT fk_alerte_hote
    FOREIGN KEY (id_hote) REFERENCES hote(id_hote)
    ON DELETE RESTRICT ON UPDATE CASCADE,

  CONSTRAINT fk_alerte_regle
    FOREIGN KEY (id_regle) REFERENCES regle(id_regle)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =========================
-- TABLE : RAPPORT
-- (1 rapport appartient à 1 alerte ; 1 alerte a 1..N rapports)
-- =========================
CREATE TABLE rapport (
  id_rapport BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  id_alerte BIGINT UNSIGNED NOT NULL,
  format VARCHAR(50) NOT NULL,          -- ex: 'console', 'json', 'txt'
  donnees LONGTEXT NOT NULL,            -- ou JSON si tu veux forcer du JSON
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_rapport_alerte (id_alerte),

  CONSTRAINT fk_rapport_alerte
    FOREIGN KEY (id_alerte) REFERENCES alerte(id_alerte)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;