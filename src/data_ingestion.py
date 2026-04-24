"""
data_ingestion.py
-----------------
Rôle : Charger les données brutes depuis une source (fichier local, URL, Kaggle)
       et les sauvegarder dans data/raw/
Communication : Produit → data/raw/soil_water.csv (consommé par preprocess.py)
"""

import pandas as pd
import numpy as np
import os
import yaml

def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)

def generate_synthetic_data(n_samples=1000, random_state=42):
    """
    Génère un dataset réaliste de besoins en eau du sol.
    Features agronomiques : température, humidité, type de sol, etc.
    """
    np.random.seed(random_state)
    
    data = {
        "temperature": np.random.uniform(10, 45, n_samples),        # °C
        "humidity": np.random.uniform(20, 95, n_samples),           # %
        "soil_moisture": np.random.uniform(10, 60, n_samples),      # %
        "evapotranspiration": np.random.uniform(1, 12, n_samples),  # mm/day
        "rainfall": np.random.uniform(0, 50, n_samples),            # mm
        "wind_speed": np.random.uniform(0, 30, n_samples),          # km/h
        "solar_radiation": np.random.uniform(5, 30, n_samples),     # MJ/m²
        "soil_type": np.random.choice([0, 1, 2], n_samples),        # 0=sandy, 1=clay, 2=loam
        "crop_stage": np.random.choice([0, 1, 2, 3], n_samples),    # growth stage
    }
    
    df = pd.DataFrame(data)
    
    # Target réaliste : besoin en eau (mm/jour) basé sur une formule agronomique
    df["water_need"] = (
        0.6 * df["evapotranspiration"]
        + 0.3 * (df["temperature"] / 10)
        - 0.4 * (df["rainfall"] / 20)
        - 0.2 * (df["soil_moisture"] / 30)
        + 0.1 * df["solar_radiation"] / 10
        + np.random.normal(0, 0.5, n_samples)  # bruit réaliste
    ).clip(0, 15)  # entre 0 et 15 mm/jour
    
    return df

def load_from_csv(path):
    """Charge depuis un CSV existant"""
    return pd.read_csv(path)

def main():
    params = load_params()
    os.makedirs("data/raw", exist_ok=True)
    
    # Si tu as un vrai dataset, remplace ici par load_from_csv()
    df = generate_synthetic_data(
        random_state=params["data"]["random_state"]
    )
    
    output_path = "data/raw/soil_water.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print(f"   Sauvegardé dans : {output_path}")
    print(f"   Target stats:\n{df['water_need'].describe()}")

if __name__ == "__main__":
    main()