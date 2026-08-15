"""CRUD incident et requêtes liées au workflow des statuts."""

from dao.base_dao import BaseDAO
from database.connexion import connexion_bd

TRANSITIONS_AUTORISEES = {
    "OUVERT": {"EN_COURS", "ANNULE"},
    "EN_COURS": {"RESOLU"},
    "RESOLU": {"FERME"},
    "FERME": set(),
    "ANNULE": set(),
}


class IncidentDAO(BaseDAO):
    table = "incident"

    def creer(self, titre, description, priorite, utilisateur_id):
        requete = """
            INSERT INTO incident (titre, description, priorite, statut, utilisateur_id)
            VALUES (%s, %s, %s, 'OUVERT', %s)
        """
        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, (titre.strip(), description.strip(), priorite, utilisateur_id))
            return curseur.lastrowid

    def lister_par_utilisateur(self, utilisateur_id, statut=None, priorite=None):
        requete = "SELECT * FROM incident WHERE utilisateur_id = %s"
        parametres = [utilisateur_id]

        if statut:
            requete += " AND statut = %s"
            parametres.append(statut)
        if priorite:
            requete += " AND priorite = %s"
            parametres.append(priorite)

        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, tuple(parametres))
            return curseur.fetchall()

    def lister_ouverts_ou_en_cours(self):
        requete = "SELECT * FROM incident WHERE statut IN ('OUVERT', 'EN_COURS')"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            return curseur.fetchall()

    def a_des_interventions(self, incident_id):
        requete = "SELECT COUNT(*) AS total FROM intervention WHERE incident_id = %s"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (incident_id,))
            return curseur.fetchone()["total"] > 0

    def changer_statut(self, incident_id, nouveau_statut):
        ligne = self.get_by_id(incident_id)
        if ligne is None:
            return False, "Incident introuvable."

        statut_actuel = ligne["statut"]

        if nouveau_statut not in TRANSITIONS_AUTORISEES.get(statut_actuel, set()):
            return False, f"Transition {statut_actuel} → {nouveau_statut} interdite."

        requete = "UPDATE incident SET statut = %s WHERE id = %s"
        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, (nouveau_statut, incident_id))

        return True, f"Statut passé à {nouveau_statut}."