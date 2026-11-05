import pandas as pd
from donnees import charger_donnees

# Charger les données
df = charger_donnees()

print("=" * 50)
print("INSPECTION DU DATASET ATLAS COMMERCE")
print("=" * 50)

# 1. Afficher les 5 premières lignes
print("\n1. Les 5 premières lignes :")
print(df.head())

# 2. Dimensions du dataset
print("\n2. Dimensions du dataset :")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# 3. Informations générales
print("\n3. Informations générales :")
df.info()

# 4. Vérifier les valeurs manquantes
print("\n4. Valeurs manquantes :")
print(df.isnull().sum())

# 5. Vérifier les doublons
print("\n5. Nombre de doublons :")
print(df.duplicated().sum())

# 6. Statistiques descriptives
print("\n6. Statistiques descriptives :")
print(df.describe())

# 7. Vérifier les types de données
print("\n7. Types des colonnes :")
print(df.dtypes)

# 8. Vérifier les valeurs uniques
print("\n8. Nombre de valeurs uniques par colonne :")
print(df.nunique())

print("\n" + "=" * 50)
print("FIN DE L'INSPECTION")
print("=" * 50)