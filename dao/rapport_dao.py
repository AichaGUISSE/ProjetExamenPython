"""Requêtes d'agrégation pour les rapports et statistiques de l'ADMIN."""

from database.connexion import connexion_bd

STATUTS = ["OUVERT", "EN_COURS", "RESOLU", "FERME", "ANNULE"]
PRIORITES = ["BASSE", "MOYENNE", "HAUTE", "CRITIQUE"]


class RapportDAO:
    def compter_incidents_par_statut(self):
        requete = "SELECT statut, COUNT(*) AS total FROM incident GROUP BY statut"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            comptes = {ligne["statut"]: ligne["total"] for ligne in curseur.fetchall()}
        return [(statut, comptes.get(statut, 0)) for statut in STATUTS]

    def compter_incidents_par_priorite(self):
        requete = "SELECT priorite, COUNT(*) AS total FROM incident GROUP BY priorite"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            comptes = {ligne["priorite"]: ligne["total"] for ligne in curseur.fetchall()}
        return [(priorite, comptes.get(priorite, 0)) for priorite in PRIORITES]

    def temps_moyen_resolution_heures(self):
        requete = """
            SELECT AVG(TIMESTAMPDIFF(HOUR, i.date_creation, dernieres.date_resolution)) AS moyenne
            FROM incident i
            JOIN (
                SELECT incident_id, MAX(date_intervention) AS date_resolution
                FROM intervention
                GROUP BY incident_id
            ) dernieres ON dernieres.incident_id = i.id
            WHERE i.statut IN ('RESOLU', 'FERME')
        """
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            return curseur.fetchone()["moyenne"]

    def top_techniciens(self, limite=3):
        requete = """
            SELECT u.nom, u.prenom, COUNT(*) AS total_interventions
            FROM intervention iv
            JOIN utilisateur u ON u.id = iv.technicien_id
            GROUP BY u.id, u.nom, u.prenom
            ORDER BY total_interventions DESC
            LIMIT %s
        """
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (limite,))
            return curseur.fetchall()

    def stats_par_technicien(self):
        requete = """
            SELECT
                u.nom,
                u.prenom,
                COUNT(DISTINCT iv.incident_id) AS nb_incidents_traites,
                AVG(iv.duree_minutes) AS duree_moyenne_minutes
            FROM utilisateur u
            JOIN intervention iv ON iv.technicien_id = u.id
            WHERE u.role = 'TECHNICIEN'
            GROUP BY u.id, u.nom, u.prenom
            ORDER BY nb_incidents_traites DESC
        """
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            return curseur.fetchall()

    def taux_resolution_48h(self):
        requete = """
            SELECT
                COUNT(*) AS total_resolus,
                SUM(CASE WHEN TIMESTAMPDIFF(HOUR, i.date_creation, dernieres.date_resolution) <= 48
                         THEN 1 ELSE 0 END) AS resolus_48h
            FROM incident i
            JOIN (
                SELECT incident_id, MAX(date_intervention) AS date_resolution
                FROM intervention
                GROUP BY incident_id
            ) dernieres ON dernieres.incident_id = i.id
            WHERE i.statut IN ('RESOLU', 'FERME')
        """
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            resultat = curseur.fetchone()

        total = resultat["total_resolus"] or 0
        dans_les_48h = resultat["resolus_48h"] or 0

        if total == 0:
            return total, dans_les_48h, 0.0

        return total, dans_les_48h, (dans_les_48h / total) * 100