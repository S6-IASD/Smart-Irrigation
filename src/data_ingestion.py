"""
data_ingestion.py
-----------------
Rôle : Charger les données brutes depuis différentes sources :
       - dataset local (CSV)
       - dataset externe (URL / Kaggle)
       - fallback dataset synthétique
       puis les sauvegarder dans data/raw/

Communication : Produit → data/raw/soil_water.csv
"""

import pandas as pd
import numpy as np
import os
import yaml


# =========================
# PARAMS
# =========================
def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


# =========================
# SYNTHETIC DATA (fallback)
# =========================
def generate_synthetic_data(n_samples=1000, random_state=42):
    np.random.seed(random_state)

    data = {
        "temperature": np.random.uniform(10, 45, n_samples),
        "humidity": np.random.uniform(20, 95, n_samples),
        "soil_moisture": np.random.uniform(10, 60, n_samples),
        "evapotranspiration": np.random.uniform(1, 12, n_samples),
        "rainfall": np.random.uniform(0, 50, n_samples),
        "wind_speed": np.random.uniform(0, 30, n_samples),
        "solar_radiation": np.random.uniform(5, 30, n_samples),
        "soil_type": np.random.choice([0, 1, 2], n_samples),
        "crop_stage": np.random.choice([0, 1, 2, 3], n_samples),
    }

    df = pd.DataFrame(data)

    df["water_need"] = (
        0.6 * df["evapotranspiration"]
        + 0.3 * (df["temperature"] / 10)
        - 0.4 * (df["rainfall"] / 20)
        - 0.2 * (df["soil_moisture"] / 30)
        + 0.1 * df["solar_radiation"] / 10
        + np.random.normal(0, 0.5, n_samples)
    ).clip(0, 15)

    return df


# =========================
# LOAD LOCAL DATASET
# =========================
def load_from_csv(path):
    return pd.read_csv(path)


# =========================
# LOAD EXTERNAL DATASET
# =========================
def load_from_url(url):
    return pd.read_csv(url)


# =========================
# MAIN LOGIC (SMART SWITCH)
# =========================
def main():

    params = load_params()
    os.makedirs("data/raw", exist_ok=True)

    # =========================
    # CAS 1 : dataset local
    # =========================
    local_path = "data/raw/soil_water.csv"

    if os.path.exists(local_path):
        print("📌 Dataset local détecté → chargement...")
        df = load_from_csv(local_path)

    # =========================
    # CAS 2 : dataset URL (optionnel)
    # =========================
    elif "dataset_url" in params.get("data", {}):
        print("📌 Dataset URL détecté → chargement...")
        df = load_from_url(params["data"]["dataset_url"])

    # =========================
    # CAS 3 : fallback synthetic
    # =========================
    else:
        print("📌 Aucun dataset trouvé → génération synthétique...")
        df = generate_synthetic_data(
            random_state=params["data"]["random_state"]
        )

    # =========================
    # SAVE RAW DATA
    # =========================
    output_path = "data/raw/soil_water.csv"
    df.to_csv(output_path, index=False)

    print("\n✅ Dataset prêt")
    print(f"   Shape: {df.shape}")
    print(f"   Saved in: {output_path}")
    print(f"   Target stats:\n{df['water_need'].describe()}")


if __name__ == "__main__":
    main()