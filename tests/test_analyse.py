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


class TestAnalyse(unittest.TestCase):

    def test_repete(self):
        vus = set()
        s = sig()
        self.assertFalse(est_repete(s, vus))
        self.assertTrue(est_repete(s, vus))

    def test_evaluer_panne_en_boucle(self):
        s = sig()
        self.assertEqual(evaluer(s, 4), "BLOQUANT")
        self.assertEqual(evaluer(s, 3), "MAJEUR")


if __name__ == "__main__":
    unittest.main()