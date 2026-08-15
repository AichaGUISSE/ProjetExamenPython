"""Classe abstraite regroupant les méthodes génériques d'accès aux données."""

from abc import ABC

from database.connexion import connexion_bd


class BaseDAO(ABC):
    """Chaque DAO concret doit définir `table` (et `colonne_id` si different de 'id')."""

    table: str
    colonne_id: str = "id"

    def get_all(self):
        requete = f"SELECT * FROM {self.table}"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete)
            return curseur.fetchall()

    def get_by_id(self, identifiant):
        requete = f"SELECT * FROM {self.table} WHERE {self.colonne_id} = %s"
        with connexion_bd.lecture() as curseur:
            curseur.execute(requete, (identifiant,))
            return curseur.fetchone()

    def delete_by_id(self, identifiant):
        requete = f"DELETE FROM {self.table} WHERE {self.colonne_id} = %s"
        with connexion_bd.transaction() as curseur:
            curseur.execute(requete, (identifiant,))
            return curseur.rowcount > 0