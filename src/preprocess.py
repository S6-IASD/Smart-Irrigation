"""
preprocess.py
-------------
Rôle : Nettoyer les données, créer des features, splitter train/test
Communication : Consomme data/raw/ → Produit data/processed/
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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
    print(f"   Valeurs manquantes:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"   Doublons: {df.duplicated().sum()}")

def preprocess(df, params):
    target = params["data"]["target_column"]
    
    # Séparer features et target
    X = df.drop(columns=[target])
    y = df[target]
    
    # Supprimer doublons et NaN
    mask = ~(X.isnull().any(axis=1) | y.isnull())
    X, y = X[mask], y[mask]
    
    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=params["data"]["test_size"],
        random_state=params["data"]["random_state"]
    )
    
    # Standardisation (important pour Linear Regression)
    if params["preprocessing"]["scale_features"]:
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train),
            columns=X_train.columns
        )
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test),
            columns=X_test.columns
        )
        # Sauvegarder le scaler pour predict.py
        os.makedirs("models", exist_ok=True)
        joblib.dump(scaler, "models/scaler.pkl")
        print("   ✅ Scaler sauvegardé dans models/scaler.pkl")
    else:
        X_train_scaled, X_test_scaled = X_train, X_test
    
    return X_train_scaled, X_test_scaled, y_train, y_test

def main():
    params = load_params()
    os.makedirs("data/processed", exist_ok=True)
    
    df = pd.read_csv("data/raw/soil_water.csv")
    check_data_quality(df)
    
    X_train, X_test, y_train, y_test = preprocess(df, params)
    
    # Sauvegarder les splits
    X_train.to_csv("data/processed/X_train.csv", index=False)
    X_test.to_csv("data/processed/X_test.csv", index=False)
    y_train.to_csv("data/processed/y_train.csv", index=False)
    y_test.to_csv("data/processed/y_test.csv", index=False)
    
    print(f"✅ Preprocessing terminé:")
    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")

if __name__ == "__main__":
    main()