"""Tests unitaires de l'Agent 3 (Notification)."""

import unittest
from src.contrat import Diagnostic, Signal
from src.notification import (
    approuver,
    choisir_canal,
    composer,
    consigner,
    diffuser,
)


def generer_signal_diag(critique: bool = True, niveau: str = "BLOQUANT"):
    sig = Signal(
        ref="SH-0125",
        date="2026-11-27T17:02:11Z",
        origine="PAIEMENT",
        service="paiement",
        env="production",
        categorie="JOURNAL",
        gravite="MAJEUR",
        texte="timeout passerelle apres 30s",
    )
    diag = Diagnostic(
        signal_ref="SH-0125",
        niveau=niveau,
        cause="Passerelle lente",
        action="Isoler le service paiement",
        critique=critique,
        origines=["PAIEMENT"],
    )
    return sig, diag


class TestNotification(unittest.TestCase):

    def test_choisir_canal_valides(self):
        """Vérifie le routage vers le bon canal selon le niveau."""
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MAJEUR"), "TEAMS")
        self.assertEqual(choisir_canal("MODERE"), "EMAIL")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_choisir_canal_invalide(self):
        """Vérifie qu'une valeur de niveau inconnue lève une ValueError."""
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_composer_format(self):
        """Vérifie la présence des 5 champs et des retours à la ligne."""
        sig, diag = generer_signal_diag()
        texte = composer(sig, diag)
        lignes = texte.split("\n")
        self.assertEqual(len(lignes), 5)
        self.assertTrue(lignes[0].startswith("*** BLOQUANT ***"))
        self.assertIn("Constat: timeout passerelle", lignes[1])
        self.assertIn("Cause: Passerelle lente", lignes[2])
        self.assertIn("A faire: Isoler le service paiement", lignes[3])
        self.assertIn("Origines: PAIEMENT", lignes[4])

    def test_diffuser(self):
        """Vérifie la création du message et le passage à l'état DIFFUSE."""
        sig, diag = generer_signal_diag()
        registre = []
        msg = diffuser(sig, diag, registre)

        self.assertEqual(len(registre), 1)
        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(msg.destinataire, "astreinte-shop")
        self.assertEqual(sig.etat, "DIFFUSE")

    def test_approuver_action_critique(self):
        """Vérifie la validation humaine pour les actions critiques."""
        _, diag_critique = generer_signal_diag(critique=True)
        self.assertTrue(approuver(diag_critique, "o"))
        self.assertTrue(approuver(diag_critique, " OUI "))
        self.assertTrue(approuver(diag_critique, "ok"))
        self.assertTrue(approuver(diag_critique, "yes"))
        self.assertFalse(approuver(diag_critique, "n"))
        self.assertFalse(approuver(diag_critique, "refus"))

    def test_approuver_action_non_critique(self):
        """Vérifie qu'une action non critique est autorisée par défaut."""
        _, diag_non_critique = generer_signal_diag(critique=False)
        self.assertTrue(approuver(diag_non_critique, "n'importe quoi"))

    def test_consigner(self):
        """Vérifie l'enregistrement dans le carnet d'audit."""
        _, diag = generer_signal_diag()
        carnet = []
        entree = consigner(
            diag=diag,
            accord=True,
            responsable="astreinte-shop",
            carnet=carnet,
            instant="2026-11-27T17:10:00Z",
        )
        self.assertEqual(len(carnet), 1)
        self.assertEqual(entree["ref"], "SH-0125")
        self.assertTrue(entree["accord"])
        self.assertEqual(entree["responsable"], "astreinte-shop")


if __name__ == "__main__":
    unittest.main()