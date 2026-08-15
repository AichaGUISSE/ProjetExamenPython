"""CRUD intervention (ajout d'une intervention par un technicien)."""

from dao.base_dao import BaseDAO
from database.connexion import connexion_bd


class InterventionDAO(BaseDAO):
    table = "intervention"

    def ajouter(self, commentaire, duree_minutes, incident_id, technicien_id):
        requete = """
            INSERT INTO intervention (commentaire, duree_minutes, incident_id, technicien_id)
            VALUES (%s, %s, %s, %s)
        """
        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, (commentaire.strip(), duree_minutes, incident_id, technicien_id))
            return curseur.lastrowid

    def lister_par_incident(self, incident_id):
        requete = "SELECT * FROM intervention WHERE incident_id = %s ORDER BY date_intervention"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (incident_id,))
            return curseur.fetchall()

    def lister_par_technicien(self, technicien_id):
        requete = "SELECT * FROM intervention WHERE technicien_id = %s ORDER BY date_intervention DESC"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (technicien_id,))
            return curseur.fetchall()