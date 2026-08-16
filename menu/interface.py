"""Menus affichés selon le rôle de l'utilisateur connecté."""

from mysql.connector.errors import IntegrityError

from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from dao.utilisateur_dao import UtilisateurDAO
from menu.utils import (
    demander_choix_parmi,
    demander_email,
    demander_entier,
    demander_non_vide,
)

incident_dao = IncidentDAO()
intervention_dao = InterventionDAO()
utilisateur_dao = UtilisateurDAO()

ROLES = [
    ("ADMIN", "Admin"),
    ("UTILISATEUR", "Utilisateur"),
    ("TECHNICIEN", "Technicien"),
]

PRIORITES = [
    ("BASSE", "Basse"),
    ("MOYENNE", "Moyenne"),
    ("HAUTE", "Haute"),
    ("CRITIQUE", "Critique"),
]

STATUTS_FILTRABLES = [
    ("OUVERT", "Ouvert"),
    ("EN_COURS", "En cours"),
    ("RESOLU", "Résolu"),
    ("FERME", "Fermé"),
]


def menu_utilisateur(utilisateur):
    while True:
        print("\n--- MENU UTILISATEUR ---")
        print("1. Créer un incident")
        print("2. Voir mes incidents")
        print("3. Filtrer mes incidents par statut")
        print("0. Se déconnecter")
        choix = input("Choix : ").strip()

        if choix == "1":
            titre = demander_non_vide("Titre : ")
            description = demander_non_vide("Description : ")
            priorite = demander_choix_parmi("Priorité :", PRIORITES)

            try:
                incident_id = incident_dao.creer(titre, description, priorite, utilisateur.id)
                print(f"Incident n°{incident_id} créé.")
            except Exception as erreur:
                print(f"Impossible de créer l'incident : {erreur}")

        elif choix == "2":
            resultats = incident_dao.lister_par_utilisateur(utilisateur.id)
            if not resultats:
                print("Aucun incident pour l'instant.")
            for incident in resultats:
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "3":
            statut = demander_choix_parmi("Filtrer par statut :", STATUTS_FILTRABLES)
            resultats = incident_dao.lister_par_utilisateur(utilisateur.id, statut=statut)
            if not resultats:
                print("Aucun incident avec ce statut.")
            for incident in resultats:
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "0":
            return
        else:
            print("Choix invalide.")


def menu_technicien(utilisateur):
    while True:
        print("\n--- MENU TECHNICIEN ---")
        print("1. Voir les incidents ouverts / en cours")
        print("2. Prendre en charge un incident")
        print("3. Ajouter une intervention")
        print("4. Résoudre un incident")
        print("5. Fermer un incident résolu")
        print("0. Se déconnecter")
        choix = input("Choix : ").strip()

        if choix == "1":
            resultats = incident_dao.lister_ouverts_ou_en_cours()
            if not resultats:
                print("Aucun incident ouvert ou en cours.")
            for incident in resultats:
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "2":
            incident_id = demander_entier("ID de l'incident : ")
            ok, message = incident_dao.changer_statut(incident_id, "EN_COURS")
            print(message)

        elif choix == "3":
            incident_id = demander_entier("ID de l'incident : ")
            incident = incident_dao.get_by_id(incident_id)

            if incident is None:
                print("Incident introuvable.")
                continue
            if incident["statut"] not in ("OUVERT", "EN_COURS"):
                print("Intervention impossible : l'incident n'est ni OUVERT ni EN_COURS.")
                continue

            commentaire = demander_non_vide("Commentaire : ")
            duree = demander_entier("Durée (minutes) : ")

            try:
                intervention_dao.ajouter(commentaire, duree, incident_id, utilisateur.id)
                print("Intervention ajoutée.")
            except Exception as erreur:
                print(f"Impossible d'ajouter l'intervention : {erreur}")

        elif choix == "4":
            incident_id = demander_entier("ID de l'incident : ")
            ok, message = incident_dao.changer_statut(incident_id, "RESOLU")
            print(message)

        elif choix == "5":
            incident_id = demander_entier("ID de l'incident : ")
            ok, message = incident_dao.changer_statut(incident_id, "FERME")
            print(message)

        elif choix == "0":
            return
        else:
            print("Choix invalide.")


def menu_admin(utilisateur):
    while True:
        print("\n--- MENU ADMIN ---")
        print("1. Fonctions technicien")
        print("2. Lister tous les utilisateurs")
        print("3. Créer un utilisateur")
        print("4. Modifier un utilisateur")
        print("5. Supprimer un utilisateur")
        print("6. Rechercher un utilisateur")
        print("0. Se déconnecter")
        choix = input("Choix : ").strip()

        if choix == "1":
            menu_technicien(utilisateur)

        elif choix == "2":
            for u in utilisateur_dao.get_all():
                print(f"#{u['id']} {u['login']} - {u['nom']} {u['prenom']} ({u['role']})")

        elif choix == "3":
            login = demander_non_vide("Login : ")
            password = demander_non_vide("Mot de passe : ")
            nom = demander_non_vide("Nom : ")
            prenom = demander_non_vide("Prénom : ")
            email = demander_email("Email : ")
            role = demander_choix_parmi("Rôle :", ROLES)
            service = demander_non_vide("Service : ")

            try:
                nouvel_id = utilisateur_dao.creer(login, password, nom, prenom, email, role, service)
                print(f"Utilisateur n°{nouvel_id} créé.")
            except IntegrityError:
                print("Impossible de créer cet utilisateur : le login ou l'email existe déjà.")
            except Exception as erreur:
                print(f"Erreur lors de la création : {erreur}")

        elif choix == "4":
            utilisateur_id = demander_entier("ID à modifier : ")

            if utilisateur_dao.get_by_id(utilisateur_id) is None:
                print("Aucun utilisateur trouvé avec cet ID.")
                continue

            nom = demander_non_vide("Nouveau nom : ")
            prenom = demander_non_vide("Nouveau prénom : ")
            email = demander_email("Nouvel email : ")
            role = demander_choix_parmi("Nouveau rôle :", ROLES)
            service = demander_non_vide("Nouveau service : ")

            try:
                utilisateur_dao.modifier(utilisateur_id, nom, prenom, email, role, service)
                print("Utilisateur modifié.")
            except IntegrityError:
                print("Impossible de modifier : cet email est déjà utilisé par un autre compte.")
            except Exception as erreur:
                print(f"Erreur lors de la modification : {erreur}")

        elif choix == "5":
            utilisateur_id = demander_entier("ID à supprimer : ")
            ok, message = utilisateur_dao.supprimer_si_possible(utilisateur_id)
            print(message)

        elif choix == "6":
            terme = demander_non_vide("Rechercher (nom/login/service) : ")
            resultats = utilisateur_dao.rechercher(terme)
            if not resultats:
                print("Aucun résultat.")
            for u in resultats:
                print(f"#{u['id']} {u['login']} - {u['nom']} {u['prenom']} ({u['role']})")

        elif choix == "0":
            return
        else:
            print("Choix invalide.")


def afficher_menu(utilisateur):
    """Point d'entrée : redirige vers le bon menu selon le rôle."""
    if utilisateur.role == "ADMIN":
        menu_admin(utilisateur)
    elif utilisateur.role == "TECHNICIEN":
        menu_technicien(utilisateur)
    else:
        menu_utilisateur(utilisateur)