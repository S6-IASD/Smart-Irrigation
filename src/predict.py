"""
predict.py
----------
Rôle : Charger le meilleur modèle et faire une prédiction sur de nouvelles données
Communication : Consomme models/best_model.pkl + models/scaler.pkl
"""

import joblib
import pandas as pd
import numpy as np

def predict(input_data: dict):
    """
    input_data : dict avec les mêmes features que l'entraînement
    """
    # Charger modèle et scaler
    model = joblib.load("models/best_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    
    # Convertir en DataFrame
    df = pd.DataFrame([input_data])
    
    # Appliquer le même preprocessing
    df_scaled = scaler.transform(df)
    
    # Prédiction
    prediction = model.predict(df_scaled)[0]
    return prediction

if __name__ == "__main__":
    # Exemple de prédiction
    sample = {
        "temperature": 35.0,
        "humidity": 60.0,
        "soil_moisture": 25.0,
        "evapotranspiration": 7.5,
        "rainfall": 5.0,
        "wind_speed": 15.0,
        "solar_radiation": 20.0,
        "soil_type": 1,
        "crop_stage": 2
    }
    
    result = predict(sample)
    print(f"💧 Besoin prédit en eau: {result:.2f} mm/jour")