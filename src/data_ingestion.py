"""
data_ingestion.py
-----------------
Rôle : Copier les datasets produits par le DataOps
       vers data/raw/ pour les rendre disponibles au pipeline MLOps.

Communication : Source  → D:/MLOPS/Smart-Irrigation/dataops/data/processed/
               Produit  → data/raw/data_arbres.csv
                          data/raw/data_masse.csv
"""

import shutil
import os
import yaml


def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    params = load_params()
    os.makedirs("data/raw", exist_ok=True)

    print("\n" + "="*50)
    print("  DATA INGESTION – Smart Irrigation")
    print("="*50)

    for dataset_name in ["arbres", "masse"]:
        src = params[dataset_name]["source_path"]
        dst = f"data/raw/data_{dataset_name}.csv"

        print(f"\n── {dataset_name.upper()} ──────────────────────────")
        print(f"   Source : {src}")
        print(f"   Dest   : {dst}")

        shutil.copy2(src, dst)
        size_mb = os.path.getsize(dst) / 1_000_000
        print(f"   ✅ Copié ({size_mb:.1f} MB)")

    print("\n✅ Ingestion terminée → data/raw/ prêt pour preprocess.py")


if __name__ == "__main__":
    main()