import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RACINE_PROJET = Path(__file__).resolve().parent.parent
load_dotenv(RACINE_PROJET / ".env")


@dataclass(frozen=True)
class ConfigurationBD:
    hote: str
    port: int
    nom_base: str
    utilisateur: str
    mot_de_passe: str

    @classmethod
    def charger(cls):
        noms_obligatoires = ("DB_NAME", "DB_USER")
        manquantes = [nom for nom in noms_obligatoires if not os.getenv(nom)]

        if manquantes:
            raise ValueError(
                "Variables manquantes dans .env : " + ", ".join(manquantes)
            )

        return cls(
            hote=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            nom_base=os.environ["DB_NAME"],
            utilisateur=os.environ["DB_USER"],
            mot_de_passe=os.getenv("DB_PASSEWORD",""),
        )