from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
import random
import os

# ============================================================
# CONFIGURATION
# ============================================================
OWM_API_KEY = os.getenv("OWM_API_KEY")
DATA_DIR    = os.path.expanduser("~/Desktop/MLOps/airflow/data")
os.makedirs(DATA_DIR, exist_ok=True)

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


# ============================================================
# TÂCHE 1 — COLLECTE
# ============================================================
def collecter_donnees(**context):
    date_hier = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    tous_les_df = []

    for region_nom, infos in REGIONS.items():
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        params = {
            "parameters": "T2M,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M,EVPTRNS",
            "community":  "AG",
            "longitude":  infos["lon"],
            "latitude":   infos["lat"],
            "start":      date_hier,
            "end":        date_hier,
            "format":     "JSON"
        }

        try:
            response = requests.get(url, params=params, timeout=60)
            data = response.json()

            if "properties" not in data:
                continue

            p = data["properties"]["parameter"]
            date_str = list(p["T2M"].keys())[0]

            row = {
                "date":               pd.to_datetime(date_str, format="%Y%m%d").strftime("%Y-%m-%d"),
                "region":             region_nom,
                "latitude":           infos["lat"],
                "longitude":          infos["lon"],
                "temperature":        list(p["T2M"].values())[0],
                "humidite_air":       list(p["RH2M"].values())[0],
                "precipitations":     list(p["PRECTOTCORR"].values())[0],
                "rayonnement":        list(p["ALLSKY_SFC_SW_DWN"].values())[0],
                "vitesse_vent":       list(p["WS2M"].values())[0],
                "evapotranspiration": list(p["EVPTRNS"].values())[0],
            }

            # OWM temps réel
            try:
                owm_resp = requests.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={"lat": infos["lat"], "lon": infos["lon"], "appid": OWM_API_KEY, "units": "metric"},
                    timeout=10
                ).json()
                if owm_resp.get("cod") == 200:
                    row["temperature"]    = owm_resp["main"]["temp"]
                    row["humidite_air"]   = owm_resp["main"]["humidity"]
                    row["precipitations"] = owm_resp.get("rain", {}).get("1h", 0)
                    row["vitesse_vent"]   = owm_resp["wind"]["speed"]
            except Exception:
                pass

            # Capteurs simulés
            random.seed(42)
            plante = random.choice(infos["plantes"])
            stades = list(PLANTES[plante]["kc"].keys())
            etp    = row.get("evapotranspiration", 0) or 0
            stade  = random.choice(stades)
            kc     = PLANTES[plante]["kc"].get(stade, 1.0)

            row.update({
                "type_plante":              plante,
                "besoin_eau_annuel_mm":     PLANTES[plante]["besoin_eau_mm"],
                "stade_croissance":         stade,
                "type_sol":                 random.choice(SOLS),
                "humidite_sol":             round(random.uniform(15, 75), 1),
                "besoin_eau_journalier_mm": round(max(0, etp * kc - row["precipitations"]), 2),
            })

            tous_les_df.append(row)

        except Exception as e:
            print(f"Erreur {region_nom} : {e}")
            continue

    df = pd.DataFrame(tous_les_df)
    fichier = os.path.join(DATA_DIR, f"data_raw_{date_hier}.csv")
    df.to_csv(fichier, index=False)
    context["ti"].xcom_push(key="fichier_nouveau", value=fichier)
    print(f"✅ Collecte terminée : {len(df)} lignes → {fichier}")


# ============================================================
# TÂCHE 2 — NETTOYAGE
# ============================================================
def nettoyer_donnees(**context):
    fichier_nouveau = context["ti"].xcom_pull(key="fichier_nouveau")
    fichier_clean   = os.path.join(DATA_DIR, "data_clean.csv")

    df_nouveau = pd.read_csv(fichier_nouveau)

    if os.path.exists(fichier_clean):
        df_existant = pd.read_csv(fichier_clean)
        df = pd.concat([df_existant, df_nouveau], ignore_index=True)
    else:
        df = df_nouveau

    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates(subset=["date", "region", "type_plante"])

    cols_num = ["temperature", "humidite_air", "precipitations",
                "rayonnement", "vitesse_vent", "evapotranspiration",
                "humidite_sol", "besoin_eau_journalier_mm"]

    for col, (min_val, max_val) in LIMITES.items():
        masque = (df[col] < min_val) | (df[col] > max_val)
        if masque.sum() > 0:
            df.loc[masque, col] = df.loc[~masque, col].median()

    for col in cols_num:
        if df[col].isnull().sum() > 0:
            df[col] = df.groupby("region")[col].transform(
                lambda x: x.interpolate(method="linear", limit_direction="both")
            )

    df = df.sort_values(["region", "date"]).reset_index(drop=True)
    df.to_csv(fichier_clean, index=False)
    context["ti"].xcom_push(key="nb_lignes", value=len(df))
    print(f"✅ Nettoyage terminé : {len(df)} lignes → {fichier_clean}")


# ============================================================
# TÂCHE 3 — VALIDATION
# ============================================================
def valider_donnees(**context):
    fichier_clean = os.path.join(DATA_DIR, "data_clean.csv")
    df = pd.read_csv(fichier_clean)
    nb_lignes = context["ti"].xcom_pull(key="nb_lignes")
    erreurs = []

    if (df["humidite_air"] > 100).any():
        erreurs.append("humidite_air > 100")
    if (df["precipitations"] < 0).any():
        erreurs.append("precipitations négatives")
    if (df["besoin_eau_journalier_mm"] < 0).any():
        erreurs.append("besoin_eau négatif")

    plantes_inconnues = set(df["type_plante"].unique()) - set(PLANTES.keys())
    if plantes_inconnues:
        erreurs.append(f"plantes inconnues : {plantes_inconnues}")

    print(f"📅 Date         : {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📊 Total lignes : {nb_lignes}")
    print(f"📍 Régions      : {df['region'].nunique()}")
    print(f"🌱 Plantes      : {df['type_plante'].nunique()}")
    print(f"💧 Besoin moyen : {df['besoin_eau_journalier_mm'].mean():.2f} mm/jour")

    if erreurs:
        raise ValueError(f"Validation échouée : {erreurs}")

    print("✅ Toutes les validations sont passées !")


# ============================================================
# DÉFINITION DU DAG
# ============================================================
default_args = {
    "owner":        "dataops",
    "retries":      3,
    "retry_delay":  timedelta(minutes=5),
}

with DAG(
    dag_id="irrigation_pipeline",
    default_args=default_args,
    description="Pipeline DataOps — Irrigation Intelligente Maroc",
    schedule="0 6 * * *",        # tous les jours à 6h00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dataops", "irrigation", "maroc"],
) as dag:

    tache_collecte = PythonOperator(
        task_id="collecter_donnees",
        python_callable=collecter_donnees,
    )

    tache_nettoyage = PythonOperator(
        task_id="nettoyer_donnees",
        python_callable=nettoyer_donnees,
    )

    tache_validation = PythonOperator(
        task_id="valider_donnees",
        python_callable=valider_donnees,
    )

    tache_collecte >> tache_nettoyage >> tache_validation
