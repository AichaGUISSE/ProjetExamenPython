"""Recherche d'un utilisateur et vérification de son mot de passe."""

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