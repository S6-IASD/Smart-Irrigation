"""
phase1_collecte.py
==================
Collecte des données agro-météorologiques par VILLE (Maroc).

Sources :
  - Météo France / Open-Meteo  → données météo historiques et temps réel
  - NASA POWER                 → ET0 (évapotranspiration de référence)
  - Simulation IoT             → humidite_sol, temperature_sol, N, P, K

Colonnes produites :
    date, ville, latitude, longitude,
    T_min, T_max, pluie_mm, vent_kmh, ensoleillement_h,
    mois, type_plante, stade, humidite_sol, temperature_sol,
    N, P, K, kc, ET0, superficie_ha,
    eau_litres, eau_mm
"""

import requests
import pandas as pd
import numpy as np
import random
from datetime import datetime, date
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================
# CONFIGURATION — VILLES
# ============================================================
VILLES = {
    "Casablanca":   {"lat": 33.589, "lon": -7.603},
    "Rabat":        {"lat": 34.020, "lon": -6.841},
    "Marrakech":    {"lat": 31.631, "lon": -8.008},
    "Fès":          {"lat": 34.033, "lon": -5.000},
    "Meknès":       {"lat": 33.895, "lon": -5.554},
    "Agadir":       {"lat": 30.427, "lon": -9.598},
    "Tanger":       {"lat": 35.769, "lon": -5.800},
    "Oujda":        {"lat": 34.689, "lon": -1.908},
    "Kenitra":      {"lat": 34.261, "lon": -6.580},
    "Tétouan":      {"lat": 35.570, "lon": -5.370},
    "Safi":         {"lat": 32.299, "lon": -9.237},
    "El_Jadida":    {"lat": 33.256, "lon": -8.507},
    "Béni_Mellal":  {"lat": 32.340, "lon": -6.360},
    "Nador":        {"lat": 35.174, "lon": -2.929},
    "Settat":       {"lat": 33.001, "lon": -7.619},
    "Khouribga":    {"lat": 32.886, "lon": -6.906},
    "Ouarzazate":   {"lat": 30.919, "lon": -6.893},
    "Errachidia":   {"lat": 31.929, "lon": -4.424},
    "Laâyoune":     {"lat": 27.153, "lon": -13.203},
    "Dakhla":       {"lat": 23.684, "lon": -15.957},
    "Guelmim":      {"lat": 28.987, "lon": -10.057},
    "Zagora":       {"lat": 30.332, "lon": -5.838},
    "Chefchaouen":  {"lat": 35.171, "lon": -5.265},
    "Ifrane":       {"lat": 33.533, "lon": -5.107},
}

VILLES_PLANTES = {
    "Casablanca":   ["Blé", "Maïs", "Betterave", "Chou", "Oignon"],        # Courgette → Chou
    "Rabat":        ["Blé", "Maïs", "Betterave", "Oranger", "Laitue"],      # Haricot_vert → Laitue
    "Marrakech":    ["Olivier", "Tomate", "Oignon", "Ail", "Carotte"],       # Rose_damas, Safran → Ail, Carotte
    "Fès":          ["Blé", "Pomme_de_terre", "Oignon", "Olivier", "Betterave"],  # ✅ already valid
    "Meknès":       ["Blé", "Orge", "Olivier", "Vigne", "Pomme_de_terre"],   # ✅ already valid
    "Agadir":       ["Tomate", "Oranger", "Citronnier", "Laitue", "Oignon"], # Avocat, Courgette → Citronnier, Laitue
    "Tanger":       ["Tomate", "Chou", "Laitue", "Oranger", "Vigne"],        # Poivron, Courgette → Chou, Laitue
    "Oujda":        ["Blé", "Orge", "Olivier", "Vigne", "Oranger"],          # ✅ already valid
    "Kenitra":      ["Blé", "Maïs", "Betterave", "Oranger", "Laitue"],       # Haricot_vert → Laitue
    "Tétouan":      ["Tomate", "Carotte", "Laitue", "Oranger", "Vigne"],     # Poivron, Courgette → Carotte, Laitue
    "Safi":         ["Blé", "Maïs", "Olivier", "Betterave", "Oignon"],       # ✅ already valid
    "El_Jadida":    ["Blé", "Maïs", "Betterave", "Chou", "Carotte"],         # ✅ already valid
    "Béni_Mellal":  ["Blé", "Maïs", "Betterave", "Olivier", "Pomme_de_terre"], # ✅ already valid
    "Nador":        ["Blé", "Orge", "Olivier", "Vigne", "Oranger"],          # ✅ already valid
    "Settat":       ["Blé", "Maïs", "Betterave", "Tournesol", "Colza"],      # ✅ already valid
    "Khouribga":    ["Blé", "Orge", "Tournesol", "Betterave", "Oignon"],     # ✅ already valid
    "Ouarzazate":   ["Dattier", "Amandier", "Grenadier", "Orge", "Tomate"],  # Safran → Tomate
    "Errachidia":   ["Dattier", "Amandier", "Grenadier", "Orge", "Laitue"],  # Safran → Laitue
    "Laâyoune":     ["Dattier", "Orge", "Tomate", "Oignon", "Laitue"],       # ✅ already valid
    "Dakhla":       ["Tomate", "Laitue", "Carotte", "Chou", "Oignon"],       # Poivron, Melon, Pastèque → Laitue, Carotte, Chou
    "Guelmim":      ["Dattier", "Amandier", "Oranger", "Orge", "Oignon"],    # Arganier → Oignon
    "Zagora":       ["Dattier", "Amandier", "Grenadier", "Orge", "Laitue"],  # Henné, Safran → Laitue
    "Chefchaouen":  ["Blé", "Figuier", "Noyer", "Vigne", "Carotte"],         # ✅ already valid
    "Ifrane":       ["Blé", "Pomme_de_terre", "Orge", "Noyer", "Laitue"],    # ✅ already valid
}

# ============================================================
# PLANTES — Kc par stade (3 niveaux : jeune / mature / fin)
# ET besoin en eau annuel (mm)
# ============================================================
PLANTES = {
    # Arboriculture
    "Olivier":        {"besoin_mm": 600,  "kc": {"jeune": 0.45, "mature": 0.70, "fin": 0.65}},
    "Amandier":       {"besoin_mm": 220,  "kc": {"jeune": 0.45, "mature": 0.90, "fin": 0.65}},
    "Figuier":        {"besoin_mm": 350,  "kc": {"jeune": 0.50, "mature": 0.85, "fin": 0.65}},
    "Grenadier":      {"besoin_mm": 250,  "kc": {"jeune": 0.50, "mature": 0.90, "fin": 0.65}},
    "Oranger":        {"besoin_mm": 900,  "kc": {"jeune": 0.70, "mature": 0.75, "fin": 0.70}},
    "Citronnier":     {"besoin_mm": 850,  "kc": {"jeune": 0.70, "mature": 0.75, "fin": 0.70}},
    "Vigne":          {"besoin_mm": 400,  "kc": {"jeune": 0.30, "mature": 0.85, "fin": 0.45}},
    "Dattier":        {"besoin_mm": 180,  "kc": {"jeune": 0.90, "mature": 1.00, "fin": 0.95}},
    "Noyer":          {"besoin_mm": 700,  "kc": {"jeune": 0.50, "mature": 1.10, "fin": 0.65}},
    # Céréales
    "Blé":            {"besoin_mm": 350,  "kc": {"jeune": 0.30, "mature": 1.15, "fin": 0.25}},
    "Maïs":           {"besoin_mm": 650,  "kc": {"jeune": 0.30, "mature": 1.20, "fin": 0.60}},
    "Orge":           {"besoin_mm": 270,  "kc": {"jeune": 0.30, "mature": 1.15, "fin": 0.25}},
    "Soja":           {"besoin_mm": 450,  "kc": {"jeune": 0.40, "mature": 1.15, "fin": 0.50}},
    "Riz":            {"besoin_mm": 1200, "kc": {"jeune": 1.05, "mature": 1.20, "fin": 0.90}},
    "Sorgo":          {"besoin_mm": 400,  "kc": {"jeune": 0.30, "mature": 1.00, "fin": 0.55}},
    "Millet":         {"besoin_mm": 350,  "kc": {"jeune": 0.30, "mature": 1.00, "fin": 0.30}},
    "Avoine":         {"besoin_mm": 300,  "kc": {"jeune": 0.30, "mature": 1.15, "fin": 0.25}},
    "Seigle":         {"besoin_mm": 270,  "kc": {"jeune": 0.30, "mature": 1.15, "fin": 0.25}},
    # Oléagineux / industriels
    "Tournesol":      {"besoin_mm": 600,  "kc": {"jeune": 0.35, "mature": 1.15, "fin": 0.35}},
    "Colza":          {"besoin_mm": 400,  "kc": {"jeune": 0.35, "mature": 1.10, "fin": 0.35}},
    "Arachide":       {"besoin_mm": 500,  "kc": {"jeune": 0.40, "mature": 1.15, "fin": 0.60}},
    "Coton":          {"besoin_mm": 700,  "kc": {"jeune": 0.45, "mature": 1.20, "fin": 0.50}},
    # Racines / tubercules
    "Betterave":      {"besoin_mm": 450,  "kc": {"jeune": 0.35, "mature": 1.20, "fin": 0.70}},
    "Canne":          {"besoin_mm": 1500, "kc": {"jeune": 0.40, "mature": 1.25, "fin": 0.75}},
    "Pomme_de_terre": {"besoin_mm": 500,  "kc": {"jeune": 0.50, "mature": 1.15, "fin": 0.75}},
    "Manioc":         {"besoin_mm": 800,  "kc": {"jeune": 0.30, "mature": 1.00, "fin": 0.50}},
    # Légumes / maraîchage
    "Tomate":         {"besoin_mm": 600,  "kc": {"jeune": 0.60, "mature": 1.15, "fin": 0.80}},
    "Oignon":         {"besoin_mm": 450,  "kc": {"jeune": 0.70, "mature": 1.05, "fin": 0.75}},
    "Ail":            {"besoin_mm": 350,  "kc": {"jeune": 0.70, "mature": 1.00, "fin": 0.70}},
    "Carotte":        {"besoin_mm": 400,  "kc": {"jeune": 0.70, "mature": 1.05, "fin": 0.95}},
    "Chou":           {"besoin_mm": 380,  "kc": {"jeune": 0.70, "mature": 1.05, "fin": 0.95}},
    "Laitue":         {"besoin_mm": 250,  "kc": {"jeune": 0.70, "mature": 1.00, "fin": 0.95}},
    "Café":           {"besoin_mm": 1200, "kc": {"jeune": 0.90, "mature": 1.05, "fin": 1.00}},
}

STADES  = ["jeune", "mature", "fin"]
# SOLS    = ["argileux", "sableux", "limoneux", "argilo-limoneux", "calcaire"]

PERIODES = [
    ("2019-01-01", "2019-12-31"),
    ("2020-01-01", "2020-12-31"),
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
]

# ============================================================
# SOURCE 1 : Open-Meteo (archive historique, gratuit, Météo France
#            utilise les mêmes modèles ERA5 / AROME)
# ============================================================
def get_openmeteo_historique(ville, lat, lon, start, end):
    """
    Récupère les données météo historiques via Open-Meteo Archive API.
    Variables : T_min, T_max, pluie, vent, ensoleillement.
    Compatible avec les modèles ERA5 utilisés par Météo-France.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":        lat,
        "longitude":       lon,
        "start_date":      start,
        "end_date":        end,
        "daily":           [
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_sum",
            "wind_speed_10m_max",
            "sunshine_duration",
        ],
        "wind_speed_unit": "kmh",
        "timezone":        "Africa/Casablanca",
    }
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        d = r.json().get("daily", {})
        df = pd.DataFrame({
            "date":             d["time"],
            "ville":            ville,
            "latitude":         lat,
            "longitude":        lon,
            "T_min":            d["temperature_2m_min"],
            "T_max":            d["temperature_2m_max"],
            "pluie_mm":         d["precipitation_sum"],
            "vent_kmh":         d["wind_speed_10m_max"],
            "ensoleillement_h": [round(v / 3600, 2) if v is not None else None
                                 for v in d["sunshine_duration"]],
        })
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        return df
    except Exception as e:
        print(f"  [Open-Meteo historique] {ville} {start}→{end} : {e}")
        return None


def get_openmeteo_temps_reel(ville, lat, lon):
    """Données du jour via Open-Meteo forecast (accès gratuit)."""
    url = "https://api.open-meteo.com/v1/forecast"
    today = date.today().isoformat()
    params = {
        "latitude":        lat,
        "longitude":       lon,
        "daily":           [
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_sum",
            "wind_speed_10m_max",
            "sunshine_duration",
        ],
        "wind_speed_unit": "kmh",
        "timezone":        "Africa/Casablanca",
        "start_date":      today,
        "end_date":        today,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        d = r.json().get("daily", {})
        return {
            "date":             today,
            "ville":            ville,
            "latitude":         lat,
            "longitude":        lon,
            "T_min":            d["temperature_2m_min"][0],
            "T_max":            d["temperature_2m_max"][0],
            "pluie_mm":         d["precipitation_sum"][0],
            "vent_kmh":         d["wind_speed_10m_max"][0],
            "ensoleillement_h": round(d["sunshine_duration"][0] / 3600, 2)
                                if d["sunshine_duration"][0] is not None else None,
        }
    except Exception as e:
        print(f"  [Open-Meteo temps réel] {ville} : {e}")
        return None


# ============================================================
# SOURCE 2 : NASA POWER → ET0
# ============================================================
def get_et0_nasa(lat, lon, start, end):
    """
    ET0 (mm/jour) depuis NASA POWER (EVPTRNS).
    start/end au format YYYYMMDD.
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "EVPTRNS",
        "community":  "AG",
        "longitude":  lon,
        "latitude":   lat,
        "start":      start.replace("-", ""),
        "end":        end.replace("-", ""),
        "format":     "JSON",
    }
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        p = r.json()["properties"]["parameter"]["EVPTRNS"]
        return {
            pd.to_datetime(k, format="%Y%m%d").strftime("%Y-%m-%d"): v
            for k, v in p.items()
        }
    except Exception as e:
        print(f"  [NASA ET0] {lat},{lon} {start}→{end} : {e}")
        return {}


# ============================================================
# SOURCE 3 : Simulation IoT
# ============================================================
def simuler_capteurs_iot(df_meteo, ville, plantes_ville):
    """
    Simule les mesures capteurs IoT sol et les paramètres agronomiques.
    Génère : humidite_sol, temperature_sol, N, P, K, superficie_ha, stade, type_plante.
    """
    rng = np.random.default_rng(seed=abs(hash(ville)) % (2**31))
    n   = len(df_meteo)

    # Température sol ≈ T_moy + bruit
    T_moy = (df_meteo["T_min"].values + df_meteo["T_max"].values) / 2

    rows = []
    for i, (_, row) in enumerate(df_meteo.iterrows()):
        plante = plantes_ville[i % len(plantes_ville)]
        stade  = rng.choice(STADES)
        rows.append({
            "date":            row["date"],
            "ville":           ville,
            "mois":            int(row["date"][5:7]),
            "type_plante":     plante,
            "stade":           stade,
            # "type_sol":        rng.choice(SOLS),
            "humidite_sol":    round(float(rng.uniform(15, 75)), 1),
            "temperature_sol": round(float(T_moy[i] + rng.uniform(-3, 3)), 1),
            "N":               round(float(rng.uniform(0, 200)), 1),   # kg/ha
            "P":               round(float(rng.uniform(0, 100)), 1),   # kg/ha
            "K":               round(float(rng.uniform(0, 150)), 1),   # kg/ha
            "superficie_ha":   round(float(rng.uniform(0.5, 50)), 2),  # ha
        })
    return pd.DataFrame(rows)


# ============================================================
# CALCUL AGRONOMIQUE
# ============================================================
def calculer_colonnes_agro(df):
    """
    Ajoute kc, ET0, eau_mm, eau_litres.
      - kc      : coefficient cultural selon plante et stade
      - ET0     : évapotranspiration de référence (colonne déjà présente)
      - eau_mm  : besoin net journalier (mm) = ET0 * kc − pluie  (≥ 0)
      - eau_litres : volume pour toute la superficie (1 mm = 10 000 L/ha)
    """
    def get_kc(row):
        p = PLANTES.get(row["type_plante"])
        if p is None:
            return None
        return p["kc"].get(row["stade"], 1.0)

    df["kc"] = df.apply(get_kc, axis=1)

    def get_eau_mm(row):
        if row["ET0"] is None or row["kc"] is None:
            return None
        return round(max(0.0, row["ET0"] * row["kc"] - row["pluie_mm"]), 2)

    df["eau_mm"] = df.apply(get_eau_mm, axis=1)

    def get_eau_litres(row):
        if row["eau_mm"] is None:
            return None
        return round(row["eau_mm"] * 10000 * row["superficie_ha"], 0)

    df["eau_litres"] = df.apply(get_eau_litres, axis=1)
    return df


# ============================================================
# COLLECTE PRINCIPALE
# ============================================================
def collecter_toutes_villes():
    tous = []

    for ville, coords in VILLES.items():
        lat, lon          = coords["lat"], coords["lon"]
        plantes_ville     = VILLES_PLANTES.get(ville, list(PLANTES.keys())[:5])
        print(f"\n▶ {ville} ({lat}, {lon})")

        # 1. Météo historique
        dfs_meteo = []
        for start, end in PERIODES:
            df_m = get_openmeteo_historique(ville, lat, lon, start, end)
            if df_m is not None:
                dfs_meteo.append(df_m)

        # 2. Données temps réel (aujourd'hui)
        reel = get_openmeteo_temps_reel(ville, lat, lon)
        if reel:
            dfs_meteo.append(pd.DataFrame([reel]))

        if not dfs_meteo:
            print(f"  ⚠ Aucune donnée météo pour {ville}, ignoré.")
            continue

        df_meteo = pd.concat(dfs_meteo, ignore_index=True)
        df_meteo = df_meteo.drop_duplicates(subset=["date", "ville"])
        print(f"  Météo : {len(df_meteo)} jours")

        # 3. ET0 NASA (on récupère par période)
        et0_map = {}
        for start, end in PERIODES:
            et0_map.update(get_et0_nasa(lat, lon, start, end))
        df_meteo["ET0"] = df_meteo["date"].map(et0_map)

        # 4. Capteurs IoT simulés
        df_iot = simuler_capteurs_iot(df_meteo, ville, plantes_ville)

        # 5. Fusion
        df = pd.merge(df_meteo, df_iot, on=["date", "ville"])

        # 6. Calculs agronomiques
        df = calculer_colonnes_agro(df)

        tous.append(df)

    return pd.concat(tous, ignore_index=True)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)

    df = collecter_toutes_villes()

    # Ordre final des colonnes
    colonnes = [
        "date", "ville", "latitude", "longitude",
        "T_min", "T_max", "pluie_mm", "vent_kmh", "ensoleillement_h",
        "mois", "type_plante", "stade",
        "humidite_sol", "temperature_sol",
        "N", "P", "K",
        "kc", "ET0", "superficie_ha",
        "eau_litres", "eau_mm",
        # colonnes conservées mais non exigées en sortie finale
        # "type_sol",
    ]
    colonnes_presentes = [c for c in colonnes if c in df.columns]
    df = df[colonnes_presentes]

    sortie = "data/raw/data_raw.csv"
    df.to_csv(sortie, index=False)
    print(f"\n✅ {sortie} sauvegardé : {len(df)} lignes × {len(df.columns)} colonnes")
    print(df.dtypes)
