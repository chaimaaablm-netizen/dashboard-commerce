
"""Preparation, filtrage et indicateurs de ventes Atlas Commerce."""

from pathlib import Path
import pandas as pd

# 1. Charger le fichier CSV
CHEMIN = Path(__file__).resolve().parent / "sales_data_brut.csv"
BRUT = pd.read_csv(CHEMIN, encoding="utf-8-sig")

# 2. Verifier les colonnes obligatoires
REQUIS = [
    "Ligne_ID", "Commande_ID", "Date", "Produit", "Categorie",
    "Region", "Quantite", "Prix_Unitaire", "Cout_Unitaire",
    "Remise_Pct", "Chiffre_Affaires",
]

absentes = set(REQUIS) - set(BRUT.columns)

if absentes:
    raise ValueError(f"Colonnes manquantes : {sorted(absentes)}")

# 3. Supprimer les doublons
df = BRUT.drop_duplicates(subset="Ligne_ID").copy()

# 4. Convertir les types de donnees
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

for colonne in [
    "Quantite",
    "Prix_Unitaire",
    "Cout_Unitaire",
    "Remise_Pct",
    "Chiffre_Affaires",
]:
    df[colonne] = pd.to_numeric(df[colonne], errors="coerce")

# 5. Supprimer les valeurs manquantes ou invalides
df = df.dropna(subset=REQUIS).copy()

df = df[
    (df["Quantite"] > 0)
    & (df["Prix_Unitaire"] > 0)
    & (df["Cout_Unitaire"] >= 0)
    & (df["Remise_Pct"].between(0, 1))
].copy()

# 6. Verifier le chiffre d'affaires
ca_recalcule = (
    df["Quantite"] * df["Prix_Unitaire"] * (1 - df["Remise_Pct"])
).round(2)

df = df[
    (df["Chiffre_Affaires"] - ca_recalcule).abs() <= 0.01
].copy()

# 7. Calculer la marge
df["Marge"] = (
    df["Chiffre_Affaires"] - df["Quantite"] * df["Cout_Unitaire"]
)

df = df.sort_values("Date").reset_index(drop=True)

# 8. Statistiques de qualite
STAT_QUALITE = {
    "brutes": len(BRUT),
    "doublons": int(BRUT["Ligne_ID"].duplicated().sum()),
    "retenues": len(df),
    "exclues_total": len(BRUT) - len(df),
}

# 9. Fonction de filtrage
def filtrer(date_debut=None, date_fin=None, categorie="Toutes"):
    donnees = df

    if date_debut:
        donnees = donnees[donnees["Date"] >= pd.to_datetime(date_debut)]

    if date_fin:
        donnees = donnees[donnees["Date"] <= pd.to_datetime(date_fin)]

    if categorie and categorie != "Toutes":
        donnees = donnees[donnees["Categorie"] == categorie]

    return donnees.copy()

# 10. Fonction de calcul des KPI
def calculer_kpis(donnees):
    ca = float(donnees["Chiffre_Affaires"].sum())
    nb = int(donnees["Commande_ID"].nunique())
    marge = float(donnees["Marge"].sum())

    return {
        "ca": ca,
        "commandes": nb,
        "panier": ca / nb if nb else 0.0,
        "marge": marge,
        "taux_marque": 100 * marge / ca if ca else 0.0,
    }

# 11. Formater les montants en MAD
def mad(valeur):
    return f"{valeur:,.0f}".replace(",", " ") + " MAD"


# 12. Test du fichier
if __name__ == "__main__":
    print("QUALITE", STAT_QUALITE)
    print("TYPES\n", df.dtypes)
    print("KPI\n", calculer_kpis(df))
