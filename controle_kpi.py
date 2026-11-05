from donnees import df, filtrer, calculer_kpis

print("KPI globaux :", calculer_kpis(df))
print("Mode seule :", calculer_kpis(filtrer(categorie="Mode")))
print("Mois de janvier :", len(filtrer("2025-01-01", "2025-01-31")))
