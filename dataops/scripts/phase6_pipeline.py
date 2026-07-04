"""
DAG Airflow — Smart-Irrigation DataOps
Collecte quotidienne des prédictions validées par les utilisateurs.
Tourne chaque jour à 2h du matin.

→ Placer ce fichier dans : ~/airflow/dags/
"""

import os
import pandas as pd
import psycopg2
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "aws-0-eu-west-1.pooler.supabase.com",
    "port":     6543,
    "dbname":   "postgres",
    "user":     "postgres.golsrmfjahsginfempxb",
    "password": "pass@@##6655ggqqll",
}

PLANTES_ARBRES = {
    "Olivier", "Amandier", "Figuier", "Grenadier",
    "Oranger", "Citronnier", "Vigne", "Dattier", "Noyer"
}

PATH_ARBRES = os.path.expanduser("~/smart-irrigation/data/processed/data_arbres.csv")
PATH_MASSE  = os.path.expanduser("~/smart-irrigation/data/processed/data_masse.csv")
BACKUP_DIR  = os.path.expanduser("~/smart-irrigation/data/backup")


# ──────────────────────────────────────────────────────────────
# PIPELINE
# ──────────────────────────────────────────────────────────────
def run_pipeline():
    os.makedirs(os.path.dirname(PATH_ARBRES), exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    print("=" * 55)
    print(f"  Smart-Irrigation DataOps — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)

    # ── 1. EXTRACT ────────────────────────────────────────────
    print("[1/5] Extraction depuis PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT
            p.ville, p.latitude, p.longitude, p.superficie_ha,
            p.type_plante, p.stade,
            m.date, m.mois, m."T_min", m."T_max", m.pluie_mm,
            c.humidite_sol, c.temperature_sol, c."N", c."P", c."K",
            pr.quantite_reelle, pr.unite
        FROM prediction_prediction pr
        JOIN parcelles_parcelle           p ON pr.parcelle_id = p.id
        LEFT JOIN meteo_donneemeteo       m ON pr.meteo_id    = m.id
        LEFT JOIN capteurs_lecturecapteur c ON pr.lecture_id  = c.id
        WHERE pr.quantite_reelle IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"         {len(df)} lignes extraites")

    # ── 2. CLEAN ──────────────────────────────────────────────
    print("[2/5] Nettoyage & validation...")
    initial = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=["type_plante", "quantite_reelle", "T_min", "T_max", "mois"])
    for col in ["humidite_sol", "temperature_sol", "N", "P", "K", "pluie_mm"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    df = df[df["T_max"] > df["T_min"]]
    df = df[df["quantite_reelle"] > 0]
    df = df[df["superficie_ha"] > 0]
    print(f"         {initial} → {len(df)} lignes après nettoyage")

    # ── 3. FEATURE ENGINEERING ────────────────────────────────
    print("[3/5] Feature engineering...")
    def get_saison(mois):
        if mois in [3, 4, 5]:     return "printemps"
        elif mois in [6, 7, 8]:   return "été"
        elif mois in [9, 10, 11]: return "automne"
        else:                     return "hiver"

    df["saison"]              = df["mois"].apply(get_saison)
    df["amplitude_thermique"] = (df["T_max"] - df["T_min"]).round(2)
    df["fertilite_sol"]       = (df["N"] + df["P"] + df["K"])
    print(f"         saison, amplitude_thermique, fertilite_sol")

    # ── 4. SPLIT + TARGET ─────────────────────────────────────
    print("[4/5] Séparation arbres / masse...")
    df["type_culture"] = df["type_plante"].apply(
        lambda x: "arbre" if x in PLANTES_ARBRES else "masse"
    )
    df_arbres = df[df["type_culture"] == "arbre"].copy()
    df_arbres["eau_mm"] = df_arbres["quantite_reelle"]
    df_arbres = df_arbres.drop(columns=["quantite_reelle", "unite"], errors="ignore")

    df_masse = df[df["type_culture"] == "masse"].copy()
    df_masse["eau_litres"] = df_masse["quantite_reelle"]
    df_masse = df_masse.drop(columns=["quantite_reelle", "unite"], errors="ignore")
    print(f"         Arbres : {len(df_arbres)} | Masse : {len(df_masse)}")

    # ── 5. MERGE ──────────────────────────────────────────────
    print("[5/5] Fusion avec les datasets existants...")
    timestamp = datetime.now().strftime("%Y%m%d")

    for path, df_new, name in [
        (PATH_ARBRES, df_arbres, "data_arbres"),
        (PATH_MASSE,  df_masse,  "data_masse"),
    ]:
        if os.path.exists(path):
            df_old = pd.read_csv(path)
            df_old.to_csv(f"{BACKUP_DIR}/{name}_{timestamp}.csv", index=False)
            df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates()
        else:
            df_final = df_new

        df_final.to_csv(path, index=False)
        print(f"         {name}.csv → {len(df_final)} lignes totales")

    print("=" * 55)
    print("  ✅ Pipeline terminé — datasets prêts pour MLOps")
    print("=" * 55)


# ──────────────────────────────────────────────────────────────
# DAG
# ──────────────────────────────────────────────────────────────
with DAG(
    dag_id="smart_irrigation_dataops",
    description="Collecte quotidienne des prédictions validées → datasets MLOps",
    default_args={
        "owner":            "dataops",
        "retries":          2,
        "retry_delay":      timedelta(minutes=5),
        "email_on_failure": True,
        "email":            ["dataops@smart-irrigation.com"],
    },
    start_date=datetime(2025, 1, 1),
    schedule="0 2 * * *",   # chaque jour à 2h du matin
    catchup=False,
    tags=["dataops", "smart-irrigation"],
) as dag:

    PythonOperator(
        task_id="run_dataops_pipeline",
        python_callable=run_pipeline,
    )