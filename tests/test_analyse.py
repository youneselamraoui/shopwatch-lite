import unittest
from src.analyse import compter_incidents, diagnostiquer, est_repete, evaluer
from src.contrat import FICHES, Signal


def sig(
    categorie="JOURNAL",
    gravite="MAJEUR",
    texte="timeout passerelle apres 30s",
    service="paiement",
    domaine="PAIEMENT",
):
    return Signal(
        "SH-0001",
        "2026-11-27T17:00:00Z",
        domaine,
        service,
        "production",
        categorie,
        gravite,
        texte,
    )


