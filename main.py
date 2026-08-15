"""Point de départ de l'application."""

from database.connexion import connexion_bd
from menu.auth import demander_authentification


def main():
    try:
        utilisateur = demander_authentification()

        if utilisateur is None:
            return 1

        print("Authentification réussie.")
        print("Les menus par rôle arrivent dans la prochaine étape.")
        return 0
    except Exception as erreur:
        print(f"Une erreur est survenue : {erreur}")
        return 1
    finally:
        connexion_bd.fermer()


if __name__ == "__main__":
    raise SystemExit(main())