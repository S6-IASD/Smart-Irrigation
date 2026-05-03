"""
phase2_nettoyage.py
===================
Nettoyage et validation du fichier data_raw.csv produit par phase1_collecte.py.

Étapes :
  1. Chargement et typage
  2. Traitement des valeurs manquantes (interpolation par ville)
  3. Correction des valeurs aberrantes (remplacement par médiane)
  4. Suppression des doublons
  5. Validation finale
  6. Export data_clean.csv
"""

import pandas as pd
import numpy as np

# ============================================================
# RÉFÉRENTIEL
# ============================================================
PLANTES_VALIDES = {
    "Olivier", "Amandier", "Figuier", "Grenadier", "Oranger",
    "Citronnier", "Vigne", "Dattier", "Noyer",
    "Blé", "Maïs", "Orge", "Soja", "Riz", "Sorgo", "Millet",
    "Avoine", "Seigle",
    "Tournesol", "Colza", "Arachide", "Coton",
    "Betterave", "Canne", "Pomme_de_terre", "Manioc",
    "Tomate", "Oignon", "Ail", "Carotte", "Chou", "Laitue", "Café",
}

STADES_VALIDES = {"jeune", "mature", "fin"}

# Bornes physiques acceptables
LIMITES = {
    "T_min":            (-10,  45),
    "T_max":            (  0,  55),
    "pluie_mm":         (  0, 200),
    "vent_kmh":         (  0, 150),
    "ensoleillement_h": (  0,  16),
    "humidite_sol":     (  0, 100),
    "temperature_sol":  ( -5,  60),
    "N":                (  0, 500),
    "P":                (  0, 300),
    "K":                (  0, 400),
    "kc":               (  0,   2),
    "ET0":              (  0,  20),
    "superficie_ha":    (  0, 500),
    "eau_mm":           (  0,  30),
    "eau_litres":       (  0, 1.5e8),
}

COLS_NUMERIQUES = list(LIMITES.keys())

# ============================================================
# FONCTIONS
# ============================================================

def charger_donnees(chemin="data/raw/data_raw.csv"):
    """Charge le CSV et applique les bons types."""
    df = pd.read_csv(chemin)
    df["date"]      = pd.to_datetime(df["date"])
    df["mois"]      = df["mois"].astype(int)
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    for col in COLS_NUMERIQUES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def traiter_valeurs_manquantes(df):
    """
    Interpolation linéaire par ville pour chaque variable numérique.
    Les extrémités sans voisins sont remplies par la valeur la plus proche.
    """
    for col in COLS_NUMERIQUES:
        if col not in df.columns:
            continue
        n_avant = df[col].isnull().sum()
        if n_avant > 0:
            df[col] = df.groupby("ville")[col].transform(
                lambda x: x.interpolate(method="linear", limit_direction="both")
            )
            n_apres = df[col].isnull().sum()
            if n_apres > 0:
                # Fallback : médiane globale si une ville entière manque
                mediane_globale = df[col].median()
                df[col] = df[col].fillna(mediane_globale)
            print(f"  {col:25s} : {n_avant} NaN → {df[col].isnull().sum()} restants")
    return df


def corriger_aberrants(df):
    """
    Valeurs hors bornes physiques → remplacées par la médiane de la colonne
    (calculée sur les valeurs valides).
    """
    for col, (vmin, vmax) in LIMITES.items():
        if col not in df.columns:
            continue
        masque = (df[col] < vmin) | (df[col] > vmax)
        n = masque.sum()
        if n > 0:
            mediane = df.loc[~masque, col].median()
            df.loc[masque, col] = mediane
            print(f"  {col:25s} : {n} valeurs aberrantes corrigées (médiane={mediane:.2f})")
    return df


def corriger_coherence(df):
    """
    Vérifie des cohérences physiques supplémentaires :
      - T_min doit être ≤ T_max
      - eau_mm ≥ 0
      - eau_litres ≥ 0
    """
    # T_min > T_max → on échange
    masque_t = df["T_min"] > df["T_max"]
    if masque_t.sum() > 0:
        print(f"  T_min > T_max : {masque_t.sum()} lignes échangées")
        df.loc[masque_t, ["T_min", "T_max"]] = df.loc[masque_t, ["T_max", "T_min"]].values

    # Recalcul eau_mm et eau_litres au cas où kc/ET0 ont été corrigés
    if {"ET0", "kc", "pluie_mm", "superficie_ha"}.issubset(df.columns):
        df["eau_mm"] = (df["ET0"] * df["kc"] - df["pluie_mm"]).clip(lower=0).round(2)
        df["eau_litres"] = (df["eau_mm"] * 10000 * df["superficie_ha"]).round(0)

    return df


def supprimer_doublons(df):
    """Supprime les doublons sur (date, ville, type_plante)."""
    n_avant = len(df)
    df = df.drop_duplicates(subset=["date", "ville", "type_plante"])
    print(f"  Doublons supprimés : {n_avant - len(df)}")
    return df


def valider_donnees(df):
    """
    Validation finale : retourne une liste d'erreurs (vide si tout est OK).
    """
    erreurs = []

    # Stades
    stades_inconnus = set(df["stade"].unique()) - STADES_VALIDES
    if stades_inconnus:
        erreurs.append(f"Stades inconnus : {stades_inconnus}")

    # Plantes
    plantes_inconnues = set(df["type_plante"].unique()) - PLANTES_VALIDES
    if plantes_inconnues:
        erreurs.append(f"Plantes inconnues : {plantes_inconnues}")

    # Valeurs physiquement impossibles
    for col, (vmin, vmax) in LIMITES.items():
        if col not in df.columns:
            continue
        n = ((df[col] < vmin) | (df[col] > vmax)).sum()
        if n > 0:
            erreurs.append(f"{col} : {n} valeurs hors [{vmin}, {vmax}]")

    # Cohérence T_min / T_max
    if (df["T_min"] > df["T_max"]).any():
        erreurs.append("T_min > T_max sur certaines lignes")

    # Valeurs négatives interdites
    for col in ["pluie_mm", "eau_mm", "eau_litres", "ET0", "superficie_ha"]:
        if col in df.columns and (df[col] < 0).any():
            erreurs.append(f"{col} contient des valeurs négatives")

    # NaN résiduels
    for col in COLS_NUMERIQUES:
        if col in df.columns:
            n = df[col].isnull().sum()
            if n > 0:
                erreurs.append(f"{col} : {n} NaN résiduels")

    return erreurs


def nettoyer_donnees(
    chemin_entree="data/raw/data_raw.csv",
    chemin_sortie="data/processed/data_clean.csv",
):
    import os
    os.makedirs("data/processed", exist_ok=True)

    print("=== Chargement ===")
    df = charger_donnees(chemin_entree)
    print(f"  {len(df)} lignes, {len(df.columns)} colonnes")

    print("\n=== Valeurs manquantes ===")
    df = traiter_valeurs_manquantes(df)

    print("\n=== Valeurs aberrantes ===")
    df = corriger_aberrants(df)

    print("\n=== Cohérence ===")
    df = corriger_coherence(df)

    print("\n=== Doublons ===")
    df = supprimer_doublons(df)

    df = df.sort_values(["ville", "date", "type_plante"]).reset_index(drop=True)

    print("\n=== Validation finale ===")
    erreurs = valider_donnees(df)
    if erreurs:
        for e in erreurs:
            print(f"  ❌ {e}")
        raise ValueError(f"Validation échouée ({len(erreurs)} erreur(s))")
    else:
        print("  ✅ Toutes les validations passées")

    # Ordre final des colonnes
    colonnes_finales = [
        "date", "ville", "latitude", "longitude",
        "T_min", "T_max", "pluie_mm", "vent_kmh", "ensoleillement_h",
        "mois", "type_plante", "stade",
        "humidite_sol", "temperature_sol",
        "N", "P", "K",
        "kc", "ET0", "superficie_ha",
        "eau_litres", "eau_mm",
    ]
    colonnes_presentes = [c for c in colonnes_finales if c in df.columns]
    df = df[colonnes_presentes]

    df.to_csv(chemin_sortie, index=False)
    print(f"\n✅ {chemin_sortie} sauvegardé : {len(df)} lignes × {len(df.columns)} colonnes")
    return df


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    df = nettoyer_donnees()

    print("\n--- Aperçu ---")
    print(df.head(3).to_string())
    print("\n--- Types ---")
    print(df.dtypes)
    print("\n--- Statistiques ---")
    print(df.describe().round(2).to_string())
