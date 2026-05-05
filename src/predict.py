"""
predict.py
----------
Rôle : Charger le meilleur modèle et faire une prédiction sur de nouvelles données
Communication : Consomme models/{dataset}/best_model.pkl
                           models/{dataset}/scaler.pkl
                           models/{dataset}/encoders.pkl
"""

import joblib
import pandas as pd
import numpy as np


def predict(input_data: dict, dataset: str) -> float:
    """
    input_data : dict avec les mêmes features que l'entraînement (valeurs brutes)
    dataset    : "arbres" ou "masse"
    """
    models_dir = f"models/{dataset}"

    # Charger modèle, scaler et encoders
    model    = joblib.load(f"{models_dir}/best_model.pkl")
    scaler   = joblib.load(f"{models_dir}/scaler.pkl")
    encoders = joblib.load(f"{models_dir}/encoders.pkl")

    # Convertir en DataFrame
    df = pd.DataFrame([input_data])

    # Appliquer le même encodage catégoriel (LabelEncoder)
    for col, le in encoders.items():
        if col in df.columns:
            df[col] = le.transform(df[col].astype(str))

    # Appliquer le même preprocessing (scaling)
    df_scaled = scaler.transform(df)

    # Prédiction
    prediction = model.predict(df_scaled)[0]
    return float(prediction)


if __name__ == "__main__":

    # ── Exemple 1 : arbres ────────────────────────────────────────────────
    sample_arbres = {
        "T_min":           18.0,
        "T_max":           38.0,
        "humidite_sol":    35.0,
        "temperature_sol": 28.0,
        "N":               1.2,
        "P":               0.8,
        "K":               1.5,
        "pluie_mm":        0.0,
        "type_plante":     "Oranger",
        "stade":           "mature",
    }

    result_arbres = predict(sample_arbres, dataset="arbres")
    print(f"\n🌳 [ARBRES]  Besoin en eau prédit : {result_arbres:.4f} mm/jour")

    # ── Exemple 2 : masse ─────────────────────────────────────────────────
    sample_masse = {
        "T_min":           10.0,
        "T_max":           22.0,
        "humidite_sol":    45.0,
        "temperature_sol": 18.0,
        "N":               0.9,
        "P":               0.6,
        "K":               1.0,
        "pluie_mm":        5.0,
        "type_plante":     "Blé",
        "stade":           "jeune",
        "superficie_ha":   5.0,
    }

    result_masse = predict(sample_masse, dataset="masse")
    print(f"🌾 [MASSE]   Besoin en eau prédit : {result_masse:.2f} litres")