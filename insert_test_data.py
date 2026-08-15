"""Insertion du compte administrateur de test."""

import os

from dao.utilisateur_dao import UtilisateurDAO
from database.connexion import connexion_bd


def inserer_administrateur():
    dao = UtilisateurDAO()
    login = os.getenv("ADMIN_LOGIN", "admin").strip()

    if dao.trouver_par_login(login) is not None:
        print("Le compte administrateur existe déjà.")
        return

    requete = """
        INSERT INTO utilisateur (login, password, nom, prenom, email, role, service)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valeurs = (
        login,
        os.getenv("ADMIN_PASSWORD", "Admin123!"),
        os.getenv("ADMIN_NOM", "Administrateur").strip(),
        os.getenv("ADMIN_PRENOM", "Principal").strip(),
        os.getenv("ADMIN_EMAIL", "admin@gestion.local").strip(),
        "ADMIN",
        "Informatique",
    )

    with connexion_bd.transaction() as curseur:
        curseur.execute(requete, valeurs)

    print("Compte administrateur créé.")


if __name__ == "__main__":
    try:
        inserer_administrateur()
    except Exception as erreur:
        print(f"Erreur : {erreur}")
    finally:
        connexion_bd.fermer()