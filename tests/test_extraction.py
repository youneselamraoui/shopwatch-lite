import unittest
from src.extraction import masquer_donnees, lire_journal, lire_scan, lire_build

class TestMasquerDonnees(unittest.TestCase):
    def test_remplace_password(self):
        s = 'client=bob pwd=abc123'
        self.assertEqual(masquer_donnees(s), 'client=bob pwd=[MASQUE]')

    def test_ignore_casse(self):
        s = 'Token=XYZ123 secret=abc'
        self.assertEqual(masquer_donnees(s), 'Token=[MASQUE] secret=[MASQUE]')

    def test_separateur_colon(self):
        s = 'card:4970123412341234'
        self.assertEqual(masquer_donnees(s), 'card:[MASQUE]')

class TestLireJournal(unittest.TestCase):
    def test_parsing_base(self):
        ligne = '2026-11-27 17:02:11 paiement ERROR timeout passerelle card=1234'
        sig = lire_journal(ligne, 42)
        self.assertEqual(sig.ref, 'SH-0042')
        self.assertEqual(sig.date, '2026-11-27T17:02:11Z')
        self.assertEqual(sig.servi ce, 'paiement')
        self.assertEqual(sig.categorie, 'JOURNAL')
        self.assertEqual(sig.gravite, 'MAJEUR')
        self.assertIn('card=[MASQUE]', sig.texte)

    def test_gravite_bloquant(self):
        ligne = '2026-11-27 17:00:00 svc FATAL boom'
        sig = lire_journal(ligne, 1)
        self.assertEqual(sig.gravite, 'BLOQUANT')

    def test_gravite_mineur(self):
        ligne = '2026-11-27 17:00:00 svc INFO ok'
        sig = lire_journal(ligne, 1)
        self.assertEqual(sig.gravite, 'MINEUR')

    def test_erreur_champs_insuffisants(self):
        with self.assertRaises(ValueError):
            lire_journal('2026-11-27', 1)

class TestLireScan(unittest.TestCase):
    def test_scan_critique(self):
        rapport = {'id_faille': 'CVE-1', 'paquet': 'lib', 'risque': 'critique', 'date': '2026-01-01T00:00:00Z'}
        sig = lire_scan(rapport, 5)
        self.assertEqual(sig.origine, 'SCANNER')
        self.assertEqual(sig.service, 'lib')
        self.assertEqual(sig.categorie, 'FAILLE')
        self.assertEqual(sig.gravite, 'BLOQUANT')
        self.assertEqual(sig.texte, 'Faille CVE-1 dans lib')

    def test_scan_cle_manquante(self):
        with self.assertRaises(ValueError):
            lire_scan({'id_faille': 'x'}, 1)

class TestLireBuild(unittest.TestCase):
    def test_build_echec(self):
        rapport = {'etape': 'deploiement', 'resultat': 'echec', 'date': '2026-01-01T00:00:00Z'}
        sig = lire_build(rapport, 3)
        self.assertEqual(sig.origine, 'BUILD')
        self.assertEqual(sig.categorie, 'BUILD_ECHEC')
        self.assertEqual(sig.gravite, 'MAJEUR')
        self.assertEqual(sig.texte, 'Build deploiement : echec')

    def test_build_ok(self):
        rapport = {'etape': 'test', 'resultat': 'OK', 'date': '2026-01-01T00:00:00Z'}
        sig = lire_build(rapport, 3)
        self.assertEqual(sig.categorie, 'BUILD_OK')
        self.assertEqual(sig.gravite, 'MINEUR')
