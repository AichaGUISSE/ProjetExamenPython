"""Connexion MySQL — pattern Singleton (une seule instance dans toute l'appli)."""

from contextlib import contextmanager

import mysql.connector

from database.config import ConfigurationBD


class Connexion:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connexion = None
            cls._instance.configuration = ConfigurationBD.charger()
        return cls._instance

    def ouvrir(self):
        if self._connexion is None or not self._connexion.is_connected():
            self._connexion = mysql.connector.connect(
                host=self.configuration.hote,
                port=self.configuration.port,
                database=self.configuration.nom_base,
                user=self.configuration.utilisateur,
                password=self.configuration.mot_de_passe,
                autocommit=False,
            )
        return self._connexion

    @contextmanager
    def lecture(self):
        connexion = self.ouvrir()
        curseur = connexion.cursor(dictionary=True)
        try:
            yield curseur
        finally:
            curseur.close()

    @contextmanager
    def transaction(self):
        connexion = self.ouvrir()
        curseur = connexion.cursor(dictionary=True)
        try:
            yield curseur
            connexion.commit()
        except Exception:
            connexion.rollback()
            raise
        finally:
            curseur.close()

    def fermer(self):
        if self._connexion is not None and self._connexion.is_connected():
            self._connexion.close()
        self._connexion = None


connexion_bd = Connexion()