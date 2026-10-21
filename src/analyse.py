from src.contrat import Diagnostic, Signal


def est_repete(sig: Signal, vus: set) -> bool:
    """Un signal est répété si (service, texte) a déjà été vu."""
    cle = (sig.service, sig.texte)
    if cle in vus:
        return True
    vus.add(cle)
    return False


def compter_incidents(sig: Signal, compteur: dict) -> int:
    """Incrémente et retourne le nombre d'incidents pour le service."""
    compteur[sig.service] = compteur.get(sig.service, 0) + 1
    return compteur[sig.service]


def chercher_fiches(sig: Signal, base) -> list:
    """Retourne les fiches associées à la catégorie du signal."""
    if isinstance(base, dict):
        fiches = base.get(sig.categorie, base.get(sig.service, []))
        return fiches if isinstance(fiches, list) else [fiches]
    return [f for f in base if getattr(f, "categorie", None) == sig.categorie]


def evaluer(sig: Signal, nb_incidents: int = 0) -> str:
    """BLOQUANT à partir de 4 incidents, sinon gravité d'origine."""
    if nb_incidents >= 4:
        return "BLOQUANT"
    return sig.gravite


def diagnostiquer(sig: Signal, base, nb_incidents: int = 0) -> Diagnostic:
    niveau = evaluer(sig, nb_incidents)
    fiches = chercher_fiches(sig, base)
    fiche = fiches[0] if fiches else None

    if isinstance(fiche, dict):
        cause = fiche.get("cause", "cause inconnue")
        action = fiche.get("action", "escalader a l'astreinte")
    else:
        cause = getattr(fiche, "cause", "cause inconnue")
        action = getattr(fiche, "action", "escalader a l'astreinte")

    critique = niveau in ("BLOQUANT", "CRITIQUE")

    return Diagnostic(
        signal_ref=sig.ref,
        niveau=niveau,
        cause=cause,
        action=action,
        critique=critique,
        origines=[sig.origine],
    )