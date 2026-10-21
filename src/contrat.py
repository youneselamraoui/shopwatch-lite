from dataclasses import dataclass

NIVEAUX = ["MINEUR", "MODERE", "MAJEUR", "BLOQUANT"]
FICHES = {
 "timeout": "Delai depasse : verifier la passerelle de paiement puis relancer le service.",
 "build": "Echec de build : lire le journal de l'etape puis rejouer apres correction.",
 "faille": "Faille connue : mettre a jour la dependance vers une version corrigee.",
}

@dataclass
class Signal:
 ref: str
 date: str
 origine: str
 service: str
 env: str
 categorie: str
 gravite: str
 texte: str
 etat: str = "RECU"

@dataclass
class Diagnostic:
 signal_ref: str
 niveau: str
 cause: str
 action: str
 critique: bool
 origines: list

@dataclass
class Message:
 signal_ref: str
 canal: str
 destinataire: str
 contenu: str
