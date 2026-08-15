"""Menus affichés selon le rôle de l'utilisateur connecté."""

from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from dao.utilisateur_dao import UtilisateurDAO

incident_dao = IncidentDAO()
intervention_dao = InterventionDAO()
utilisateur_dao = UtilisateurDAO()


def menu_utilisateur(utilisateur):
    while True:
        print("\n--- MENU UTILISATEUR ---")
        print("1. Créer un incident")
        print("2. Voir mes incidents")
        print("3. Filtrer mes incidents par statut")
        print("0. Quitter")
        choix = input("Choix : ").strip()

        if choix == "1":
            titre = input("Titre : ").strip()
            description = input("Description : ").strip()
            priorite = input("Priorité (BASSE/MOYENNE/HAUTE/CRITIQUE) : ").strip().upper()
            incident_id = incident_dao.creer(titre, description, priorite, utilisateur.id)
            print(f"Incident n°{incident_id} créé.")

        elif choix == "2":
            for incident in incident_dao.lister_par_utilisateur(utilisateur.id):
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "3":
            statut = input("Statut (OUVERT/EN_COURS/RESOLU/FERME) : ").strip().upper()
            for incident in incident_dao.lister_par_utilisateur(utilisateur.id, statut=statut):
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
        print("0. Quitter")
        choix = input("Choix : ").strip()

        if choix == "1":
            for incident in incident_dao.lister_ouverts_ou_en_cours():
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "2":
            incident_id = int(input("ID de l'incident : "))
            ok, message = incident_dao.changer_statut(incident_id, "EN_COURS")
            print(message)

        elif choix == "3":
            incident_id = int(input("ID de l'incident : "))
            incident = incident_dao.get_by_id(incident_id)

            if incident is None:
                print("Incident introuvable.")
                continue
            if incident["statut"] not in ("OUVERT", "EN_COURS"):
                print("Intervention impossible : l'incident n'est ni OUVERT ni EN_COURS.")
                continue

            commentaire = input("Commentaire : ").strip()
            duree = int(input("Durée (minutes) : "))
            intervention_dao.ajouter(commentaire, duree, incident_id, utilisateur.id)
            print("Intervention ajoutée.")

        elif choix == "4":
            incident_id = int(input("ID de l'incident : "))
            ok, message = incident_dao.changer_statut(incident_id, "RESOLU")
            print(message)

        elif choix == "5":
            incident_id = int(input("ID de l'incident : "))
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
        print("0. Quitter")
        choix = input("Choix : ").strip()

        if choix == "1":
            menu_technicien(utilisateur)

        elif choix == "2":
            for u in utilisateur_dao.get_all():
                print(f"#{u['id']} {u['login']} - {u['nom']} {u['prenom']} ({u['role']})")

        elif choix == "3":
            login = input("Login : ").strip()
            password = input("Mot de passe : ").strip()
            nom = input("Nom : ").strip()
            prenom = input("Prénom : ").strip()
            email = input("Email : ").strip()
            role = input("Rôle (UTILISATEUR/TECHNICIEN/ADMIN) : ").strip().upper()
            service = input("Service : ").strip()
            nouvel_id = utilisateur_dao.creer(login, password, nom, prenom, email, role, service)
            print(f"Utilisateur n°{nouvel_id} créé.")

        elif choix == "4":
            utilisateur_id = int(input("ID à modifier : "))
            nom = input("Nouveau nom : ").strip()
            prenom = input("Nouveau prénom : ").strip()
            email = input("Nouvel email : ").strip()
            role = input("Nouveau rôle : ").strip().upper()
            service = input("Nouveau service : ").strip()
            ok = utilisateur_dao.modifier(utilisateur_id, nom, prenom, email, role, service)
            print("Utilisateur modifié." if ok else "Aucun utilisateur trouvé avec cet ID.")

        elif choix == "5":
            utilisateur_id = int(input("ID à supprimer : "))
            ok, message = utilisateur_dao.supprimer_si_possible(utilisateur_id)
            print(message)

        elif choix == "6":
            terme = input("Rechercher (nom/login/service) : ").strip()
            for u in utilisateur_dao.rechercher(terme):
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