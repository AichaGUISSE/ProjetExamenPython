"""Représentation d'une intervention technicien sur un incident."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Intervention:
    id: int
    commentaire: str
    duree_minutes: int
    date_intervention: datetime
    incident_id: int
    technicien_id: int