"""Script de création des tables."""

from database.connexion import connexion_bd

CREATE_TABLE_UTILISATEUR = """
CREATE TABLE IF NOT EXISTS utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'UTILISATEUR',
    service VARCHAR(100),
    date_creation DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT ck_utilisateur_role
        CHECK (role IN ('UTILISATEUR', 'TECHNICIEN', 'ADMIN'))
);
"""

CREATE_TABLE_INCIDENT = """
CREATE TABLE IF NOT EXISTS incident (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priorite VARCHAR(20) NOT NULL DEFAULT 'MOYENNE',
    statut VARCHAR(20) NOT NULL DEFAULT 'OUVERT',
    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilisateur_id INT NOT NULL,
    CONSTRAINT fk_incident_utilisateur
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id),
    CONSTRAINT ck_incident_priorite
        CHECK (priorite IN ('BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE')),
    CONSTRAINT ck_incident_statut
        CHECK (statut IN ('OUVERT', 'EN_COURS', 'RESOLU', 'FERME', 'ANNULE'))
);
"""

CREATE_TABLE_INTERVENTION = """
CREATE TABLE IF NOT EXISTS intervention (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commentaire TEXT NOT NULL,
    duree_minutes INT NOT NULL DEFAULT 0,
    date_intervention DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    incident_id INT NOT NULL,
    technicien_id INT NOT NULL,
    CONSTRAINT fk_intervention_incident
        FOREIGN KEY (incident_id) REFERENCES incident(id),
    CONSTRAINT fk_intervention_technicien
        FOREIGN KEY (technicien_id) REFERENCES utilisateur(id),
    CONSTRAINT ck_intervention_duree
        CHECK (duree_minutes >= 0)
);
"""


def creer_tables():
    with connexion_bd.transaction() as curseur:
        curseur.execute(CREATE_TABLE_UTILISATEUR)
        curseur.execute(CREATE_TABLE_INCIDENT)
        curseur.execute(CREATE_TABLE_INTERVENTION)
    print("Tables utilisateur, incident, intervention créées (ou déjà existantes).")


if __name__ == "__main__":
    try:
        creer_tables()
    except Exception as erreur:
        print(f"Erreur lors de la création des tables : {erreur}")
    finally:
        connexion_bd.fermer()