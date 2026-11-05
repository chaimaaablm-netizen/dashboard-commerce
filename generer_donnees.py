
"""Genere un jeu de ventes fictives, avec 3 defauts volontaires."""

from datetime import date
from pathlib import Path
import random
import pandas as pd

RNG = random.Random(2026)
DOSSIER = Path(__file__).resolve().parent

CATALOGUE = {
    "Electronique": {
        "Casque Bluetooth": (320, 205),
        "Souris sans fil": (150, 75),
        "Clavier mecanique": (460, 280),
    },
    "Maison": {
        "Cafetiere": (720, 470),
        "Lampe LED": (185, 90),
        "Aspirateur": (1490, 990),
    },
    "Mode": {
        "Sac a dos": (420, 230),
        "Veste": (590, 335),
        "Baskets": (780, 455),
    },
    "Sport": {
        "Tapis de yoga": (190, 80),
        "Halteres": (350, 210),
        "Velo urbain": (2150, 1760),
    },
}

REGIONS = [
    "Casablanca-Settat", "Rabat-Sale-Kenitra", "Souss-Massa",
    "Marrakech-Safi", "Fes-Meknes", "Tanger-Tetouan-Al Hoceima",
]

POIDS_REGIONS = [31, 20, 13, 16, 12, 8]

JOURS = list(pd.date_range("2025-01-01", "2026-09-30", freq="D"))

POIDS_JOURS = [
    (1.18 if jour.year == 2026 else 1.0)
    * (1.75 if jour.month in (11, 12) else 1.0)
    * (1.10 if jour.weekday() >= 5 else 1.0)
    for jour in JOURS
]

lignes = []
ligne_id = 0

for numero in range(1, 2401):
    commande = f"CMD-{numero:05d}"
    jour = RNG.choices(JOURS, weights=POIDS_JOURS, k=1)[0]
    region = RNG.choices(REGIONS, weights=POIDS_REGIONS, k=1)[0]
    articles = RNG.randint(1, 3)

    for _ in range(articles):
        categorie = RNG.choice(list(CATALOGUE))
        produit = RNG.choice(list(CATALOGUE[categorie]))
        prix, cout = CATALOGUE[categorie][produit]
        quantite = RNG.randint(1, 4)

        remise = (
            0.10
            if jour.month in (11, 12) and categorie == "Electronique"
            else 0.0
        )

        ca = round(quantite * prix * (1 - remise), 2)
        ligne_id += 1

        lignes.append({
            "Ligne_ID": ligne_id,
            "Commande_ID": commande,
            "Date": jour.strftime("%Y-%m-%d"),
            "Produit": produit,
            "Categorie": categorie,
            "Region": region,
            "Quantite": quantite,
            "Prix_Unitaire": prix,
            "Cout_Unitaire": cout,
            "Remise_Pct": remise,
            "Chiffre_Affaires": ca,
        })

brut = pd.DataFrame(lignes)

# 3 anomalies intentionnelles
brut = pd.concat([brut, brut.iloc[[0]].copy()], ignore_index=True)
brut.loc[1, "Region"] = None
brut.loc[2, "Date"] = "date-invalide"

chemin = DOSSIER / "sales_data_brut.csv"
brut.to_csv(chemin, index=False, encoding="utf-8-sig")

print(f"CSV cree : {chemin.name}")
print(f"Lignes brutes : {len(brut)} ; commandes generees : 2400")
print("Indices : un doublon, une region manquante, une date invalide.")