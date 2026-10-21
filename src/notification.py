"""Agent 3 : Notification (ShopWatch-Lite)."""

from src.contrat import Diagnostic, Message, Signal


def choisir_canal(niveau: str) -> str:
    """Détermine le canal de notification selon la gravité de l'alerte."""
    table_canaux = {
        "BLOQUANT": "SLACK",
        "MAJEUR": "TEAMS",
        "MODERE": "EMAIL",
        "MINEUR": "TABLEAU",
    }
    if niveau not in table_canaux:
        raise ValueError(f"Niveau d'alerte inconnu : {niveau}")
    return table_canaux[niveau]


def composer(sig: Signal, diag: Diagnostic) -> str:
    """Compose le message formaté sur 5 lignes distinctes."""
    origines_formatees = " + ".join(diag.origines)
    return (
        f"*** {diag.niveau} *** Service: {sig.service}\n"
        f"Constat: {sig.texte}\n"
        f"Cause: {diag.cause}\n"
        f"A faire: {diag.action}\n"
        f"Origines: {origines_formatees}"
    )


def diffuser(sig: Signal, diag: Diagnostic, registre: list) -> Message:
    """Enregistre le message dans le registre et met à jour l'état du signal."""
    canal = choisir_canal(diag.niveau)
    contenu = composer(sig, diag)
    msg = Message(
        signal_ref=sig.ref,
        canal=canal,
        destinataire="astreinte-shop",
        contenu=contenu,
    )
    registre.append(msg)
    sig.etat = "DIFFUSE"
    return msg


def approuver(diag: Diagnostic, reponse: str) -> bool:
    """Vérification humaine (Human-in-the-loop) pour les actions critiques."""
    if not diag.critique:
        return True
    return reponse.strip().lower() in {"o", "oui", "ok", "yes"}


def consigner(
    diag: Diagnostic, accord: bool, responsable: str, carnet: list, instant: str
) -> dict:
    """Consigne la décision prise dans le journal d'audit."""
    entree = {
        "ref": diag.signal_ref,
        "action": diag.action,
        "accord": accord,
        "responsable": responsable,
        "instant": instant,
    }
    carnet.append(entree)
    return entree