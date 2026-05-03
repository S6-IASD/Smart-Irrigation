import pandas as pd

# Charger le dataset avec toutes les features
df = pd.read_csv("data/processed/data_features.csv")

# Définir les deux types de cultures
PLANTES_ARBRES = {
    "Olivier", "Amandier", "Figuier", "Grenadier",
    "Oranger", "Citronnier", "Vigne", "Dattier", "Noyer"
}

PLANTES_MASSE = {
    "Blé", "Maïs", "Orge", "Soja", "Riz", "Sorgo", "Millet",
    "Avoine", "Seigle", "Tournesol", "Colza", "Arachide", "Coton",
    "Betterave", "Canne", "Pomme_de_terre", "Manioc", "Tomate",
    "Oignon", "Ail", "Carotte", "Chou", "Laitue", "Café"
}

# Créer la colonne type_culture
df["type_culture"] = df["type_plante"].apply(
    lambda x: "arbre" if x in PLANTES_ARBRES else "masse"
)

# Séparer en 2 datasets
df_arbres = df[df["type_culture"] == "arbre"].copy()
df_masse   = df[df["type_culture"] == "masse"].copy()

# Vérification
print(f"Dataset total   : {len(df)} lignes")
print(f"  Arbres        : {len(df_arbres)} lignes  → target: eau_mm")
print(f"  Masse         : {len(df_masse)} lignes  → target: eau_litres")

# Sauvegarder
df_arbres.to_csv("data/processed/data_arbres.csv", index=False)
df_masse.to_csv("data/processed/data_masse.csv",   index=False)

print("\n✅ Séparation terminée :")
print("   data/processed/data_arbres.csv")
print("   data/processed/data_masse.csv")