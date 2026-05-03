"""
preprocess.py
-------------
Rôle : Nettoyer les données, créer des features, splitter train/test
Communication : Consomme data/raw/ → Produit data/processed/
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import os
import yaml
import joblib


def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def check_data_quality(df):
    """Rapport qualité données"""
    print("📋 Rapport qualité données:")
    print(f"   Shape: {df.shape}")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing):
        print(f"   Valeurs manquantes:\n{missing}")
    else:
        print("   Valeurs manquantes: aucune ✅")
    print(f"   Doublons: {df.duplicated().sum()}")


# ─────────────────────────────────────────────────────────────────────────────
# ENCODAGE CATÉGORIEL
# ─────────────────────────────────────────────────────────────────────────────

def encode_categoricals(X_train, X_test, cat_cols):
    """
    Label-encode les colonnes catégorielles (type_plante, stade).
    Fit uniquement sur le train → appliqué sur le test (pas de data leakage).
    Retourne X_train encodé, X_test encodé, et le dict d'encoders.
    """
    X_train = X_train.copy()
    X_test  = X_test.copy()
    encoders = {}

    for col in cat_cols:
        if col not in X_train.columns:
            continue
        le = LabelEncoder()
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        X_test[col]  = le.transform(X_test[col].astype(str))
        encoders[col] = le
        print(f"   ✅ LabelEncoder [{col}] → {list(le.classes_)}")

    return X_train, X_test, encoders


# ─────────────────────────────────────────────────────────────────────────────
# SCALING  (StandardScaler  ou  MinMaxScaler)
# ─────────────────────────────────────────────────────────────────────────────

def scale_features(X_train, X_test, method="standard"):
    """
    Standardisation  : method='standard'  → moyenne=0, écart-type=1
    Normalisation    : method='minmax'    → valeurs dans [0, 1]

    Fit uniquement sur le train → appliqué sur le test.
    """
    if method == "minmax":
        scaler = MinMaxScaler()
        print("   ℹ️  Scaler : MinMaxScaler  (normalisation  [0, 1])")
    else:
        scaler = StandardScaler()
        print("   ℹ️  Scaler : StandardScaler (standardisation µ=0, σ=1)")

    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns
    )
    return X_train_scaled, X_test_scaled, scaler


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def preprocess(df, params, dataset_name):
    """
    Pipeline complet :
      1. Sélection features + target
      2. Suppression NaN / doublons résiduels
      3. Train/Test split
      4. Encodage catégoriel (LabelEncoder)
      5. Scaling (StandardScaler ou MinMaxScaler selon params.yaml)
    """
    # ── 1. Sélection features & target ───────────────────────────────────
    cfg      = params[dataset_name]           # section 'arbres' ou 'masse'
    target   = cfg["target"]
    features = cfg["features"]

    df = df[features + [target]].copy()

    X = df[features].copy()
    y = df[target].copy()

    # ── 2. Supprimer doublons & NaN résiduels ────────────────────────────
    mask = ~(X.isnull().any(axis=1) | y.isnull())
    X, y = X[mask], y[mask]

    # ── 3. Train / Test split ─────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=params["data"]["test_size"],
        random_state=params["data"]["random_state"]
    )

    # ── 4. Encodage des variables catégorielles ───────────────────────────
    cat_cols = ["type_plante", "stade"]
    X_train, X_test, encoders = encode_categoricals(X_train, X_test, cat_cols)

    # Sauvegarder les encoders (nécessaires dans predict.py)
    models_dir = f"models/{dataset_name}"
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(encoders, f"{models_dir}/encoders.pkl")
    print(f"   ✅ Encoders sauvegardés → {models_dir}/encoders.pkl")

    # ── 5. Scaling ────────────────────────────────────────────────────────
    if params["preprocessing"]["scale_features"]:
        method = params["preprocessing"].get("scale_method", "standard")
        X_train_scaled, X_test_scaled, scaler = scale_features(
            X_train, X_test, method=method
        )
        joblib.dump(scaler, f"{models_dir}/scaler.pkl")
        print(f"   ✅ Scaler sauvegardé → {models_dir}/scaler.pkl")
    else:
        X_train_scaled, X_test_scaled = X_train, X_test

    return X_train_scaled, X_test_scaled, y_train, y_test


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    params = load_params()

    for dataset_name in ["arbres", "masse"]:
        print(f"\n{'='*50}")
        print(f"  DATASET : {dataset_name.upper()}")
        print(f"{'='*50}")

        # Chargement
        raw_path = params[dataset_name]["source_path"]
        df = pd.read_csv(raw_path)
        check_data_quality(df)

        # Preprocessing
        X_train, X_test, y_train, y_test = preprocess(df, params, dataset_name)

        # Sauvegarde des splits
        out_dir = f"data/processed/{dataset_name}"
        os.makedirs(out_dir, exist_ok=True)

        X_train.to_csv(f"{out_dir}/X_train.csv", index=False)
        X_test.to_csv(f"{out_dir}/X_test.csv",   index=False)
        y_train.to_csv(f"{out_dir}/y_train.csv",  index=False)
        y_test.to_csv(f"{out_dir}/y_test.csv",    index=False)

        print(f"\n✅ Preprocessing [{dataset_name}] terminé:")
        print(f"   Train : {X_train.shape}  |  Test : {X_test.shape}")
        print(f"   Target → mean={y_train.mean():.3f}, std={y_train.std():.3f}")


if __name__ == "__main__":
    main()