"""Représentation d'un incident."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Incident:
    id: int
    titre: str
    description: str
    priorite: str
    statut: str
    date_creation: datetime
    utilisateur_id: int