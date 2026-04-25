import requests
import pandas as pd
import random
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")

# ============================================================
# CONFIGURATION
# ============================================================
REGIONS = {
    "tanger_tetouan_al_hoceima": {"lat": 35.77, "lon": -5.80, "plantes": ["tomate", "poivron", "courgette", "agrume", "vigne"]},
    "oriental":                  {"lat": 34.68, "lon": -1.90, "plantes": ["blé", "orge", "olivier", "vigne", "agrume"]},
    "fes_meknes":                {"lat": 33.98, "lon": -5.05, "plantes": ["blé", "pomme_de_terre", "oignon", "olivier", "betterave"]},
    "rabat_sale_kenitra":        {"lat": 34.24, "lon": -6.60, "plantes": ["blé", "maïs", "betterave", "agrume", "haricot_vert"]},
    "beni_mellal_khenifra":      {"lat": 32.37, "lon": -6.36, "plantes": ["blé", "maïs", "betterave", "olivier", "pomme_de_terre"]},
    "casablanca_settat":         {"lat": 33.57, "lon": -7.59, "plantes": ["blé", "maïs", "betterave", "courgette", "oignon"]},
    "marrakech_safi":            {"lat": 31.63, "lon": -8.01, "plantes": ["olivier", "rose_damas", "safran", "tomate", "oignon"]},
    "draa_tafilalet":            {"lat": 31.05, "lon": -4.00, "plantes": ["dattier", "safran", "amandier", "grenadier", "henné"]},
    "souss_massa":               {"lat": 30.42, "lon": -9.60, "plantes": ["tomate", "agrume", "avocat", "haricot_vert", "courgette"]},
    "guelmim_oued_noun":         {"lat": 28.98, "lon": -10.05,"plantes": ["dattier", "amandier", "arganier", "orge", "henné"]},
    "laayoune_sakia_el_hamra":   {"lat": 27.15, "lon": -13.20,"plantes": ["dattier", "orge", "tomate", "courgette", "oignon"]},
    "dakhla_oued_ed_dahab":      {"lat": 23.68, "lon": -15.96,"plantes": ["tomate", "poivron", "courgette", "melon", "pastèque"]},
}

PLANTES = {
    "tomate":         {"besoin_eau_mm": 600,  "kc": {"germination": 0.60, "croissance": 0.75, "floraison": 1.15, "maturité": 0.80}},
    "oignon":         {"besoin_eau_mm": 450,  "kc": {"germination": 0.70, "croissance": 0.75, "bulbaison": 1.05, "maturité": 0.75}},
    "courgette":      {"besoin_eau_mm": 500,  "kc": {"germination": 0.50, "croissance": 0.75, "floraison": 1.00, "maturité": 0.80}},
    "blé":            {"besoin_eau_mm": 350,  "kc": {"germination": 0.30, "tallage": 0.75, "épiaison": 1.15, "maturité": 0.25}},
    "maïs":           {"besoin_eau_mm": 650,  "kc": {"germination": 0.30, "croissance": 0.75, "floraison": 1.20, "maturité": 0.60}},
    "betterave":      {"besoin_eau_mm": 450,  "kc": {"germination": 0.35, "croissance": 0.75, "grossissement": 1.20, "maturité": 0.70}},
    "pomme_de_terre": {"besoin_eau_mm": 500,  "kc": {"germination": 0.50, "croissance": 0.75, "tubérisation": 1.15, "maturité": 0.75}},
    "olivier":        {"besoin_eau_mm": 600,  "kc": {"repos": 0.65, "floraison": 0.70, "fructification": 0.70, "maturité": 0.70}},
    "agrume":         {"besoin_eau_mm": 1000, "kc": {"repos": 0.75, "floraison": 0.75, "fructification": 0.70, "maturité": 0.70}},
    "avocat":         {"besoin_eau_mm": 1200, "kc": {"croissance": 0.85, "floraison": 0.85, "fructification": 0.85, "maturité": 0.85}},
    "haricot_vert":   {"besoin_eau_mm": 350,  "kc": {"germination": 0.40, "croissance": 0.75, "floraison": 1.05, "maturité": 0.85}},
    "safran":         {"besoin_eau_mm": 150,  "kc": {"dormance": 0.30, "croissance": 0.70, "floraison": 1.00, "repos": 0.30}},
    "rose_damas":     {"besoin_eau_mm": 300,  "kc": {"repos": 0.50, "croissance": 0.85, "floraison": 1.00, "maturité": 0.85}},
    "amandier":       {"besoin_eau_mm": 220,  "kc": {"repos": 0.40, "floraison": 0.70, "fructification": 0.90, "maturité": 0.65}},
    "grenadier":      {"besoin_eau_mm": 250,  "kc": {"repos": 0.50, "floraison": 0.70, "fructification": 0.90, "maturité": 0.65}},
    "orge":           {"besoin_eau_mm": 270,  "kc": {"germination": 0.30, "tallage": 0.75, "épiaison": 1.15, "maturité": 0.25}},
    "vigne":          {"besoin_eau_mm": 400,  "kc": {"repos": 0.30, "débourrement": 0.70, "floraison": 0.85, "maturité": 0.45}},
    "poivron":        {"besoin_eau_mm": 550,  "kc": {"germination": 0.60, "croissance": 0.75, "floraison": 1.05, "maturité": 0.85}},
    "dattier":        {"besoin_eau_mm": 180,  "kc": {"repos": 0.90, "floraison": 0.95, "fructification": 1.00, "maturité": 0.95}},
    "arganier":       {"besoin_eau_mm": 100,  "kc": {"repos": 0.50, "floraison": 0.65, "fructification": 0.70, "maturité": 0.65}},
    "henné":          {"besoin_eau_mm": 280,  "kc": {"germination": 0.50, "croissance": 0.80, "floraison": 1.00, "maturité": 0.70}},
    "melon":          {"besoin_eau_mm": 400,  "kc": {"germination": 0.50, "croissance": 0.75, "floraison": 1.00, "maturité": 0.75}},
    "pastèque":       {"besoin_eau_mm": 400,  "kc": {"germination": 0.40, "croissance": 0.75, "floraison": 1.00, "maturité": 0.75}},
}

SOLS = ["argileux", "sableux", "limoneux", "argilo-limoneux", "calcaire"]

PERIODES = [
    ("20190101", "20191231"),
    ("20200101", "20201231"),
    ("20210101", "20211231"),
    ("20220101", "20221231"),
    ("20230101", "20231231"),
    ("20240101", "20241231"),
    ("20250101", "20251231"),
    ("20260101", "20260424"),
]


# ============================================================
# FONCTIONS
# ============================================================
def get_nasa_region(region_nom, lat, lon, start, end):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M,EVPTRNS",
        "community": "AG",
        "longitude": lon,
        "latitude":  lat,
        "start":     start,
        "end":       end,
        "format":    "JSON"
    }
    try:
        response = requests.get(url, params=params, timeout=60)
        data = response.json()
        if "properties" not in data:
            return None
        p = data["properties"]["parameter"]
        df = pd.DataFrame({
            "date":               list(p["T2M"].keys()),
            "region":             region_nom,
            "latitude":           lat,
            "longitude":          lon,
            "temperature":        list(p["T2M"].values()),
            "humidite_air":       list(p["RH2M"].values()),
            "precipitations":     list(p["PRECTOTCORR"].values()),
            "rayonnement":        list(p["ALLSKY_SFC_SW_DWN"].values()),
            "vitesse_vent":       list(p["WS2M"].values()),
            "evapotranspiration": list(p["EVPTRNS"].values()),
        })
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
        return df
    except Exception:
        return None


def get_owm_data(region_nom, lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("cod") != 200:
            return None
        return {
            "date":               datetime.now().strftime("%Y-%m-%d"),
            "region":             region_nom,
            "latitude":           lat,
            "longitude":          lon,
            "temperature":        data["main"]["temp"],
            "humidite_air":       data["main"]["humidity"],
            "precipitations":     data.get("rain", {}).get("1h", 0),
            "rayonnement":        None,
            "vitesse_vent":       data["wind"]["speed"],
            "evapotranspiration": None,
        }
    except Exception:
        return None


def get_capteurs_region(df_meteo, region_nom, plantes_region):
    random.seed(42)
    rows = []
    for _, row in df_meteo.iterrows():
        plante = random.choice(plantes_region)
        stades = list(PLANTES[plante]["kc"].keys())
        rows.append({
            "date":                 row["date"],
            "region":               region_nom,
            "type_plante":          plante,
            "besoin_eau_annuel_mm": PLANTES[plante]["besoin_eau_mm"],
            "stade_croissance":     random.choice(stades),
            "type_sol":             random.choice(SOLS),
            "humidite_sol":         round(random.uniform(15, 75), 1),
        })
    return pd.DataFrame(rows)


def calculer_besoin_eau(row):
    plante = row["type_plante"]
    stade  = row["stade_croissance"]
    etp    = row["evapotranspiration"]
    if plante not in PLANTES or etp is None:
        return None
    kc = PLANTES[plante]["kc"].get(stade, 1.0)
    return round(max(0, etp * kc - row["precipitations"]), 2)


def collecter_toutes_regions():
    tous_les_df = []
    for region_nom, infos in REGIONS.items():
        dfs_region = []
        for start, end in PERIODES:
            df_meteo = get_nasa_region(region_nom, infos["lat"], infos["lon"], start, end)
            if df_meteo is not None:
                dfs_region.append(df_meteo)
        if not dfs_region:
            continue
        df_region_complet = pd.concat(dfs_region, ignore_index=True)
        owm = get_owm_data(region_nom, infos["lat"], infos["lon"], OWM_API_KEY)
        if owm:
            df_region_complet = pd.concat([df_region_complet, pd.DataFrame([owm])], ignore_index=True)
        df_capteurs = get_capteurs_region(df_region_complet, region_nom, infos["plantes"])
        df_final_region = pd.merge(df_region_complet, df_capteurs, on=["date", "region"])
        df_final_region["besoin_eau_journalier_mm"] = df_final_region.apply(calculer_besoin_eau, axis=1)
        tous_les_df.append(df_final_region)
    return pd.concat(tous_les_df, ignore_index=True)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    df = collecter_toutes_regions()
    df = df[[
        "date", "region", "latitude", "longitude",
        "temperature", "humidite_air", "precipitations",
        "rayonnement", "vitesse_vent", "evapotranspiration",
        "humidite_sol", "type_sol", "type_plante",
        "stade_croissance", "besoin_eau_annuel_mm",
        "besoin_eau_journalier_mm"
    ]]
    df.to_csv("data/raw/data_raw.csv", index=False)
    print(f"✅ data_raw.csv sauvegardé : {len(df)} lignes")