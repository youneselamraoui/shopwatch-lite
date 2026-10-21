import unittest
from src.extraction import lire_journal, masquer_donnees
LIGNE = "2026-11-27 17:02:11 paiement ERROR timeout passerelle apres 30s
card=4970123412341234"
class TestExtraction(unittest.TestCase):
 def test_masquer_donnees(self):
 self.assertEqual(masquer_donnees("client=bob pwd=abc123"),
 "client=bob pwd=[MASQUE]")
 def test_lire_journal(self):
 sig = lire_journal(LIGNE, 42)
 self.assertEqual(sig.ref, "SH-0042")
 self.assertEqual(sig.date, "2026-11-27T17:02:11Z")
 self.assertEqual(sig.gravite, "MAJEUR")
 self.assertNotIn("4970123412341234", sig.texte)
if __name__ == "__main__":
 unittest.main()