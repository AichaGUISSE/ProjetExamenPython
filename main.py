"""Point de départ de l'application."""

from database.connexion import connexion_bd
from menu.auth import QUITTER, demander_authentification
from menu.interface import afficher_menu


def main():
    try:
        while True:
            resultat = demander_authentification()

            if resultat == QUITTER:
                print("À bientôt.")
                return 0

            if resultat is None:
                reponse = input("Réessayer une connexion ? (o/n) : ").strip().lower()
                if reponse != "o":
                    return 1
                continue

            afficher_menu(resultat)
            print("\nDéconnexion. Retour à l'écran de connexion.\n")

    except Exception as erreur:
        print(f"Une erreur est survenue : {erreur}")
        return 1
    finally:
        connexion_bd.fermer()


if __name__ == "__main__":
    raise SystemExit(main())