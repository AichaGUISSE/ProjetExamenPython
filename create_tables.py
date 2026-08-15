"""Script de création des tables (utilisateur pour l'instant)."""

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


def creer_tables():
    with connexion_bd.transaction() as curseur:
        curseur.execute(CREATE_TABLE_UTILISATEUR)
    print("Table utilisateur créée (ou déjà existante).")
    print("Les tables incident et intervention arrivent dans la prochaine étape.")


if __name__ == "__main__":
    try:
        creer_tables()
    except Exception as erreur:
        print(f"Erreur lors de la création des tables : {erreur}")
    finally:
        connexion_bd.fermer()