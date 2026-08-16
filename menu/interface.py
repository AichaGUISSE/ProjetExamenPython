"""Menus affichés selon le rôle de l'utilisateur connecté."""

from mysql.connector.errors import IntegrityError
from dao.rapport_dao import RapportDAO

from dao.incident_dao import IncidentDAO
from dao.intervention_dao import InterventionDAO
from dao.utilisateur_dao import UtilisateurDAO
from menu.utils import (
    afficher_tableau,
    afficher_titre,
    demander_choix_parmi,
    demander_email,
    demander_entier,
    demander_non_vide,
)

rapport_dao = RapportDAO()

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


def demander_service():
    services_existants = utilisateur_dao.lister_services()

    if not services_existants:
        return demander_non_vide("Aucun service existant. Nom du nouveau service : ")

    options = [(service, service) for service in services_existants]
    options.append(("__NOUVEAU__", "+ Ajouter un nouveau service"))

    choix = demander_choix_parmi("Service :", options)

    if choix == "__NOUVEAU__":
        return demander_non_vide("Nom du nouveau service : ")

    return choix


def selectionner_incident(incidents, message_si_vide):
    """Affiche une liste d'incidents et demande de choisir un ID parmi eux.

    Renvoie None si la liste est vide (rien à choisir) ou si l'ID saisi
    n'est pas dans la liste affichée.
    """
    if not incidents:
        print(message_si_vide)
        return None

    print()
    ids_affiches = set()
    for incident in incidents:
        print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")
        ids_affiches.add(incident["id"])

    incident_id = demander_entier("ID de l'incident à choisir : ")

    if incident_id not in ids_affiches:
        print("Cet ID ne fait pas partie de la liste affichée ci-dessus.")
        return None

    return incident_id

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
            resultats = incident_dao.lister_par_statuts(["OUVERT", "EN_COURS"])
            if not resultats:
                print("Aucun incident ouvert ou en cours.")
            for incident in resultats:
                print(f"#{incident['id']} [{incident['statut']}] {incident['titre']}")

        elif choix == "2":
            incidents = incident_dao.lister_par_statuts(["OUVERT"])
            incident_id = selectionner_incident(incidents, "Aucun incident OUVERT à prendre en charge.")
            if incident_id is None:
                continue

            ok, message = incident_dao.changer_statut(incident_id, "EN_COURS")
            print(message)

        elif choix == "3":
            incidents = incident_dao.lister_par_statuts(["OUVERT", "EN_COURS"])
            incident_id = selectionner_incident(incidents, "Aucun incident disponible pour une intervention.")
            if incident_id is None:
                continue

            # Deuxième vérification : l'affichage seul ne suffit pas, on
            # revérifie le statut réel juste avant d'écrire en base.
            incident = incident_dao.get_by_id(incident_id)
            if incident is None or incident["statut"] not in ("OUVERT", "EN_COURS"):
                print("Cet incident n'est plus disponible pour une intervention.")
                continue

            commentaire = demander_non_vide("Commentaire : ")
            duree = demander_entier("Durée (minutes) : ")

            try:
                intervention_id = intervention_dao.ajouter(commentaire, duree, incident_id, utilisateur.id)
                print(f"Intervention n°{intervention_id} ajoutée.")
            except Exception as erreur:
                print(f"Impossible d'ajouter l'intervention : {erreur}")

        elif choix == "4":
            incidents = incident_dao.lister_par_statuts(["EN_COURS"])
            incident_id = selectionner_incident(incidents, "Aucun incident EN_COURS à résoudre.")
            if incident_id is None:
                continue

            ok, message = incident_dao.changer_statut(incident_id, "RESOLU")
            print(message)

        elif choix == "5":
            incidents = incident_dao.lister_par_statuts(["RESOLU"])
            incident_id = selectionner_incident(incidents, "Aucun incident RESOLU à fermer.")
            if incident_id is None:
                continue

            ok, message = incident_dao.changer_statut(incident_id, "FERME")
            print(message)

        elif choix == "0":
            return
        else:
            print("Choix invalide.")

def afficher_statistiques():
    afficher_titre("STATISTIQUES ET RAPPORTS")

    print("Incidents par statut")
    lignes = rapport_dao.compter_incidents_par_statut()
    afficher_tableau(["Statut", "Total"], lignes)

    print("\nIncidents par priorité")
    lignes = rapport_dao.compter_incidents_par_priorite()
    afficher_tableau(["Priorité", "Total"], lignes)

    moyenne = rapport_dao.temps_moyen_resolution_heures()
    print("\nTemps moyen de résolution")
    if moyenne is None:
        print("Pas encore assez de données (aucun incident résolu avec intervention).")
    else:
        print(f"{moyenne:.1f} heure(s) en moyenne, du signalement à la dernière intervention.")

    print("\nTop 3 des techniciens les plus actifs")
    top = rapport_dao.top_techniciens(3)
    if not top:
        print("Aucune intervention enregistrée pour l'instant.")
    else:
        lignes = [(f"{t['prenom']} {t['nom']}", t["total_interventions"]) for t in top]
        afficher_tableau(["Technicien", "Interventions"], lignes)

    print("\nDétail par technicien")
    details = rapport_dao.stats_par_technicien()
    if not details:
        print("Aucune donnée disponible.")
    else:
        lignes = [
            (
                f"{d['prenom']} {d['nom']}",
                d["nb_incidents_traites"],
                f"{d['duree_moyenne_minutes']:.0f} min",
            )
            for d in details
        ]
        afficher_tableau(["Technicien", "Incidents traités", "Durée moyenne"], lignes)

    total, dans_48h, pourcentage = rapport_dao.taux_resolution_48h()
    print("\nTaux de résolution dans les 48h")
    if total == 0:
        print("Pas encore d'incident résolu pour calculer ce taux.")
    else:
        print(f"{dans_48h}/{total} incidents résolus en moins de 48h ({pourcentage:.1f}%).")
    print()


def menu_admin(utilisateur):
    while True:
        print("\n--- MENU ADMIN ---")
        print("1. Fonctions technicien")
        print("2. Lister tous les utilisateurs")
        print("3. Créer un utilisateur")
        print("4. Modifier un utilisateur")
        print("5. Supprimer un utilisateur")
        print("7. Statistiques et rapports")
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
            service = demander_service()

            try:
                nouvel_id = utilisateur_dao.creer(login, password, nom, prenom, email, role, service)
                print(f"Utilisateur n°{nouvel_id} créé.")
            except IntegrityError:
                print("Impossible de créer cet utilisateur : le login ou l'email existe déjà.")
            except Exception as erreur:
                print(f"Erreur lors de la création : {erreur}")


        elif choix == "4":

            utilisateur_id = demander_entier("ID à modifier : ")

            utilisateur_existant = utilisateur_dao.get_by_id(utilisateur_id)

            if utilisateur_existant is None:
                print("Aucun utilisateur trouvé avec cet ID.")

                continue

            nom = utilisateur_existant["nom"]

            prenom = utilisateur_existant["prenom"]

            email = utilisateur_existant["email"]

            role = utilisateur_existant["role"]

            service = utilisateur_existant["service"]

            print(f"\nUtilisateur #{utilisateur_id} : {prenom} {nom} ({role}) — {email} — {service}")

            while True:

                print("\nQuel champ modifier ?")

                print("1. Nom")

                print("2. Prénom")

                print("3. Email")

                print("4. Rôle")

                print("5. Service")

                print("6. Valider les modifications")

                print("0. Annuler")

                sous_choix = input("Choix : ").strip()

                if sous_choix == "1":

                    nom = demander_non_vide("Nouveau nom : ")

                elif sous_choix == "2":

                    prenom = demander_non_vide("Nouveau prénom : ")

                elif sous_choix == "3":

                    email = demander_email("Nouvel email : ")

                elif sous_choix == "4":

                    role = demander_choix_parmi("Nouveau rôle :", ROLES)

                elif sous_choix == "5":

                    service = demander_service()

                elif sous_choix == "6":

                    try:

                        utilisateur_dao.modifier(utilisateur_id, nom, prenom, email, role, service)

                        print("Utilisateur modifié.")

                    except IntegrityError:

                        print("Impossible de modifier : cet email est déjà utilisé par un autre compte.")

                    except Exception as erreur:

                        print(f"Erreur lors de la modification : {erreur}")

                    break

                elif sous_choix == "0":

                    print("Modification annulée.")

                    break

                else:

                    print("Choix invalide.")

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

        elif choix == "7":
            afficher_statistiques()
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