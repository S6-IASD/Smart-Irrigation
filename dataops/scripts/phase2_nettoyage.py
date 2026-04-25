import pandas as pd
import numpy as np

PLANTES = {
    "tomate", "oignon", "courgette", "blé", "maïs",
    "betterave", "pomme_de_terre", "olivier", "agrume",
    "avocat", "haricot_vert", "safran", "rose_damas",
    "amandier", "grenadier", "orge", "vigne", "poivron",
    "dattier", "arganier", "henné", "melon", "pastèque"
}

LIMITES = {
    "temperature":             (-5,  50),
    "humidite_air":            (0,  100),
    "precipitations":          (0,  150),
    "rayonnement":             (0,  400),
    "vitesse_vent":            (0,   30),
    "evapotranspiration":      (0,   15),
    "humidite_sol":            (0,  100),
    "besoin_eau_journalier_mm":(0,   20),
}

DATE_FIN_NASA = "2026-04-24"


# ============================================================
# FONCTIONS
# ============================================================
def charger_donnees(chemin="data/raw/data_raw.csv"):
    df = pd.read_csv(chemin)
    df["date"]      = pd.to_datetime(df["date"])
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    return df


def traiter_valeurs_manquantes(df):
    cols = [
        "temperature", "humidite_air", "precipitations",
        "rayonnement", "vitesse_vent", "evapotranspiration",
        "humidite_sol", "besoin_eau_journalier_mm"
    ]
    for col in cols:
        if df[col].isnull().sum() > 0:
            df[col] = df.groupby("region")[col].transform(
                lambda x: x.interpolate(method="linear", limit_direction="both")
            )
    return df


def corriger_aberrants(df):
    for col, (min_val, max_val) in LIMITES.items():
        masque = (df[col] < min_val) | (df[col] > max_val)
        if masque.sum() > 0:
            mediane = df.loc[~masque, col].median()
            df.loc[masque, col] = mediane
    return df


def supprimer_doublons(df):
    return df.drop_duplicates(subset=["date", "region", "type_plante"])


def valider_donnees(df):
    erreurs = []
    if (df["humidite_air"] > 100).any():
        erreurs.append("humidite_air > 100")
    if (df["precipitations"] < 0).any():
        erreurs.append("precipitations négatives")
    if (df["besoin_eau_journalier_mm"] < 0).any():
        erreurs.append("besoin_eau négatif")
    plantes_inconnues = set(df["type_plante"].unique()) - PLANTES
    if plantes_inconnues:
        erreurs.append(f"plantes inconnues : {plantes_inconnues}")
    return erreurs


def nettoyer_donnees(chemin_entree="data/raw/data_raw.csv",
                     chemin_sortie="data/processed/data_clean.csv"):
    df = charger_donnees(chemin_entree)
    df = traiter_valeurs_manquantes(df)
    df = corriger_aberrants(df)
    df = supprimer_doublons(df)
    df = df.sort_values(["region", "date"]).reset_index(drop=True)

    erreurs = valider_donnees(df)
    if erreurs:
        raise ValueError(f"Validation échouée : {erreurs}")

    df.to_csv(chemin_sortie, index=False)
    return df


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    df = nettoyer_donnees()
    print(f"✅ data_clean.csv sauvegardé : {len(df)} lignes")