from dataclasses import dataclass


@dataclass
class Utilisateur:
    id: int
    login: str
    nom: str
    prenom: str
    email: str
    role: str
    service: str

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"