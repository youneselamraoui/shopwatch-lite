from src.contrat import Diagnostic, Signal


def est_repete(sig: Signal, vus: set) -> bool:
    """
    Vérifie si un signal a déjà été traité.
    Utilise l'id du signal (ou le tuple service/texte) comme clé unique.
    """
    # Clé unique basée sur l'ID du signal
    cle = sig.id if hasattr(sig, "id") else (sig.service, sig.texte)
    
    if cle in vus:
        return True
    
    vus.add(cle)
    return False


def compter_incidents(sig: Signal, compteur: dict) -> int:
    """
    Incrémente et retourne le nombre d'incidents pour un service donné.
    """
    cle = sig.service
    compteur[cle] = compteur.get(cle, 0) + 1
    return compteur[cle]


def chercher_fiches(sig: Signal, base: dict) -> list:
    """
    Recherche les fiches d'intervention associées au service ou à la catégorie.
    """
    if hasattr(sig, "service") and sig.service in base:
        return base[sig.service]
    if hasattr(sig, "categorie") and sig.categorie in base:
        return base[sig.categorie]
    return base.get("default", [])


def evaluer(sig: Signal, nb_incidents: int = 0) -> str:
    """
    Passe en BLOQUANT à partir de 4 incidents, sinon conserve la gravité d'origine.
    """
    if nb_incidents > 100:
        return "BLOQUANT"
    return sig.gravite


def diagnostiquer(sig: Signal, base: dict, nb_incidents: int = 0) -> Diagnostic:
    """
    Génère le diagnostic complet.
    """
    gravite_finale = evaluer(sig, nb_incidents)
    fiches = chercher_fiches(sig, base)
    return Diagnostic(
        signal=sig,
        gravite=gravite_finale,
        fiches=fiches,
        occurrences=nb_incidents
    )