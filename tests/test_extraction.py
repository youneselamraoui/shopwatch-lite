import re
from src.contrat import Signal


def masquer_donnees(texte: str) -> str:
    """Masque mots de passe, jetons, cartes et jetons Bearer."""
    # Jeton Bearer : "Bearer xxx" devient "Bearer [MASQUE]"
    texte = re.sub(r'(Bearer\s+)\S+', r'\1[MASQUE]', texte, flags=re.IGNORECASE)
    # Paires cle=valeur / cle:valeur
    texte = re.sub(
        r'(pwd|password|token|secret|card)(\s*[=:]\s*)\S+',
        r'\1\2[MASQUE]',
        texte,
        flags=re.IGNORECASE,
    )
    return texte


def _ref(numero: int) -> str:
    return f"SH-{numero:04d}"


def lire_journal(ligne: str, numero: int) -> Signal:
    parties = ligne.split(maxsplit=4)
    if len(parties) < 5:
        raise ValueError(f"ligne de journal invalide : {ligne!r}")
    jour, heure, service, niveau, texte = parties
    niveau = niveau.upper()
    if niveau == "FATAL":
        gravite = "BLOQUANT"
    elif niveau == "ERROR":
        gravite = "MAJEUR"
    else:
        gravite = "MINEUR"
    return Signal(
        ref=_ref(numero),
        date=f"{jour}T{heure}Z",
        origine="JOURNAL",
        service=service,
        env="prod",
        categorie="JOURNAL",
        gravite=gravite,
        texte=masquer_donnees(texte),
    )


def lire_scan(rapport: dict, numero: int) -> Signal:
    try:
        id_faille = rapport["id_faille"]
        paquet = rapport["paquet"]
        risque = rapport["risque"]
        date = rapport["date"]
    except KeyError as e:
        raise ValueError(f"rapport de scan incomplet : cle manquante {e}")
    gravite = "BLOQUANT" if str(risque).lower() == "critique" else "MAJEUR"
    return Signal(
        ref=_ref(numero),
        date=date,
        origine="SCANNER",
        service=paquet,
        env="prod",
        categorie="FAILLE",
        gravite=gravite,
        texte=f"Faille {id_faille} dans {paquet}",
    )


def lire_build(rapport: dict, numero: int) -> Signal:
    try:
        etape = rapport["etape"]
        resultat = rapport["resultat"]
        date = rapport["date"]
    except KeyError as e:
        raise ValueError(f"rapport de build incomplet : cle manquante {e}")
    echec = str(resultat).lower() == "echec"
    return Signal(
        ref=_ref(numero),
        date=date,
        origine="BUILD",
        service=etape,
        env="prod",
        categorie="BUILD_ECHEC" if echec else "BUILD_OK",
        gravite="MAJEUR" if echec else "MINEUR",
        texte=f"Build {etape} : {resultat}",
    )