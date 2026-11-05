"""Controles simples de qualite et de coherence du jeu de donnees."""
from donnees import BRUT, df, STAT_QUALITE, calculer_kpis

assert BRUT.shape == (4784, 11), BRUT.shape
assert STAT_QUALITE["brutes"] == 4784
assert STAT_QUALITE["doublons"] == 1
assert STAT_QUALITE["retenues"] == 4781
assert STAT_QUALITE["exclues_total"] == 3
assert df["Ligne_ID"].is_unique
assert df["Date"].notna().all()
assert df["Region"].notna().all()
assert (df["Quantite"] > 0).all()

k = calculer_kpis(df)
assert k["commandes"] == 2400
assert round(k["ca"]) == 7671306
assert round(k["marge"]) == 2607006

print("Audit donnees : OK")
print("Qualite :", STAT_QUALITE)
print("KPI :", k)

