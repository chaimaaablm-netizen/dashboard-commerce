
import unittest
from donnees import df, filtrer, calculer_kpis


class TestAtlasCommerce(unittest.TestCase):

    def test_nombre_lignes(self):
        self.assertEqual(len(df), 4781)

    def test_nombre_commandes(self):
        k = calculer_kpis(df)
        self.assertEqual(k["commandes"], 2400)

    def test_chiffre_affaires(self):
        k = calculer_kpis(df)
        self.assertEqual(k["ca"], 7671306.0)

    def test_marge(self):
        k = calculer_kpis(df)
        self.assertEqual(k["marge"], 2607006.0)

    def test_panier_moyen(self):
        k = calculer_kpis(df)
        self.assertAlmostEqual(k["panier"], 3196.3775, places=2)

    def test_filtre_maison(self):
        ventes = filtrer(None, None, "Maison")
        self.assertFalse(ventes.empty)
        self.assertTrue((ventes["Categorie"] == "Maison").all())

    def test_filtre_toutes(self):
        ventes = filtrer(None, None, "Toutes")
        self.assertEqual(len(ventes), len(df))

    def test_filtre_date(self):
        ventes = filtrer("2024-01-01", "2024-12-31", "Toutes")
        self.assertTrue((ventes["Date"] >= "2024-01-01").all())
        self.assertTrue((ventes["Date"] <= "2024-12-31").all())

    def test_kpi_zero_si_vide(self):
        ventes = filtrer("1900-01-01", "1900-01-02", "Toutes")
        k = calculer_kpis(ventes)
        self.assertEqual(k["ca"], 0)

    def test_categories_presentes(self):
        self.assertGreater(df["Categorie"].nunique(), 0)

    def test_regions_presentes(self):
        self.assertGreater(df["Region"].nunique(), 0)

    def test_doublons(self):
        self.assertEqual(df.duplicated().sum(), 0)


if __name__ == "__main__":
    unittest.main()
