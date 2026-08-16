"""CRUD utilisateur + authentification."""

from dao.base_dao import BaseDAO
from database.connexion import connexion_bd
from models.utilisateur import Utilisateur


class UtilisateurDAO(BaseDAO):
    table = "utilisateur"

    def trouver_par_login(self, login):
        requete = """
            SELECT id, login, password, nom, prenom, email, role, service
            FROM utilisateur
            WHERE login = %s
        """
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (login.strip(),))
            return curseur.fetchone()

    def authentifier(self, login, mot_de_passe):
        ligne = self.trouver_par_login(login)

        if ligne is None:
            return None
        if ligne["password"] != mot_de_passe:
            return None

        return Utilisateur(
            id=ligne["id"],
            login=ligne["login"],
            nom=ligne["nom"],
            prenom=ligne["prenom"],
            email=ligne["email"],
            role=ligne["role"],
            service=ligne["service"],
        )

    def creer(self, login, password, nom, prenom, email, role, service):
        requete = """
            INSERT INTO utilisateur (login, password, nom, prenom, email, role, service)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valeurs = (login.strip(), password, nom.strip(), prenom.strip(),
                   email.strip(), role, service)

        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, valeurs)
            return curseur.lastrowid

    def modifier(self, utilisateur_id, nom, prenom, email, role, service):
        requete = """
            UPDATE utilisateur
            SET nom = %s, prenom = %s, email = %s, role = %s, service = %s
            WHERE id = %s
        """
        valeurs = (nom.strip(), prenom.strip(), email.strip(), role, service, utilisateur_id)

        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, valeurs)
            return curseur.rowcount > 0

    def a_des_incidents_ou_interventions(self, utilisateur_id):
        requete_incidents = "SELECT COUNT(*) AS total FROM incident WHERE utilisateur_id = %s"
        requete_interventions = "SELECT COUNT(*) AS total FROM intervention WHERE technicien_id = %s"

        with connexion_bd.lecture() as curseur:
            curseur.execute(requete_incidents, (utilisateur_id,))
            total_incidents = curseur.fetchone()["total"]

            curseur.execute(requete_interventions, (utilisateur_id,))
            total_interventions = curseur.fetchone()["total"]

        return (total_incidents + total_interventions) > 0

    def supprimer_si_possible(self, utilisateur_id):
        if self.a_des_incidents_ou_interventions(utilisateur_id):
            return False, "Suppression impossible : cet utilisateur a des incidents ou interventions associés."

        self.delete_by_id(utilisateur_id)
        return True, "Utilisateur supprimé."

    def rechercher(self, terme):
        requete = """
            SELECT id, login, nom, prenom, email, role, service
            FROM utilisateur
            WHERE nom LIKE %s OR login LIKE %s OR service LIKE %s
        """
        motif = f"%{terme.strip()}%"

        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (motif, motif, motif))
            return curseur.fetchall()

    def supprimer_si_possible(self, utilisateur_id):
        if self.get_by_id(utilisateur_id) is None:
            return False, "Aucun utilisateur trouvé avec cet ID."

        if self.a_des_incidents_ou_interventions(utilisateur_id):
            return False, "Suppression impossible : cet utilisateur a des incidents ou interventions associés."

        self.delete_by_id(utilisateur_id)
        return True, "Utilisateur supprimé."