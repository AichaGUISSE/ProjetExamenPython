"""Saisie et contrôle des informations de connexion."""

from getpass import getpass

from dao.utilisateur_dao import UtilisateurDAO


def demander_authentification():
    dao = UtilisateurDAO()
    essais_restants = 3

    print("\n=== AUTHENTIFICATION ===")

    while essais_restants > 0:
        login = input("Login : ").strip()
        mot_de_passe = getpass("Mot de passe : ")

        if not login or not mot_de_passe:
            print("Le login et le mot de passe sont obligatoires.")
            continue

        utilisateur = dao.authentifier(login, mot_de_passe)

        if utilisateur is not None:
            print(f"Bienvenue {utilisateur.nom_complet}.")
            print(f"Rôle : {utilisateur.role} — Service : {utilisateur.service}")
            return utilisateur

        essais_restants -= 1
        print("Login ou mot de passe incorrect.")
        print(f"Essais restants : {essais_restants}")

    print("Trop de tentatives. Connexion refusée.")
    return None