"""
train.py
--------
Rôle : Entraîner les 3 modèles et logger TOUT dans MLflow
Communication : Consomme data/processed/ → Produit models/{dataset}/best_model.pkl
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import joblib
import os
import yaml
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def mape(y_true, y_pred):
    """Mean Absolute Percentage Error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def compute_metrics(y_true, y_pred, model_name):
    """Calcule toutes les métriques"""
    mae      = mean_absolute_error(y_true, y_pred)
    rmse     = np.sqrt(mean_squared_error(y_true, y_pred))
    r2       = r2_score(y_true, y_pred)
    mape_val = mape(y_true, y_pred)

    print(f"\n📊 {model_name}:")
    print(f"   MAE:  {mae:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R²:   {r2:.4f}")
    print(f"   MAPE: {mape_val:.2f}%")

    return {"mae": float(mae), "rmse": float(rmse),
            "r2": float(r2), "mape": float(mape_val)}


def train_and_log(model, model_name, params_to_log,
                  X_train, X_test, y_train, y_test,
                  dataset_name):
    """Entraîne un modèle et log tout dans MLflow"""

    with mlflow.start_run(run_name=model_name):
        # Entraînement
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Métriques
        metrics = compute_metrics(y_test, y_pred, model_name)

        # ✅ Log paramètres MLflow
        mlflow.log_params(params_to_log)

        # ✅ Log métriques MLflow
        mlflow.log_metrics(metrics)

        # ✅ Log modèle MLflow
        mlflow.sklearn.log_model(model, name="model")

        # Tags pour identifier facilement
        mlflow.set_tag("model_type", model_name)
        mlflow.set_tag("dataset", dataset_name)          # ← dynamique

        run_id = mlflow.active_run().info.run_id
        print(f"   MLflow run_id: {run_id}")

    return metrics, model


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE PAR DATASET
# ─────────────────────────────────────────────────────────────────────────────

def train_dataset(dataset_name, params):
    """
    Entraîne les 3 modèles pour un dataset donné.
    Paths dynamiques : data/processed/{dataset_name}/ et models/{dataset_name}/
    """
    print(f"\n{'='*55}")
    print(f"  TRAINING – {dataset_name.upper()}")
    print(f"{'='*55}")

    # ── Chargement des splits préprocessés ───────────────────────────────
    proc_dir = f"data/processed/{dataset_name}"
    X_train  = pd.read_csv(f"{proc_dir}/X_train.csv")
    X_test   = pd.read_csv(f"{proc_dir}/X_test.csv")
    y_train  = pd.read_csv(f"{proc_dir}/y_train.csv").squeeze()
    y_test   = pd.read_csv(f"{proc_dir}/y_test.csv").squeeze()

    print(f"📂 Données chargées: Train={X_train.shape}, Test={X_test.shape}")

    # ── Expérience MLflow propre à chaque dataset ─────────────────────────
    mlflow.set_experiment(f"smart_irrigation_{dataset_name}")

    results     = {}
    trained_models = {}

    # ── 1. BASELINE : Linear Regression ──────────────────────────────────
    lr_model = LinearRegression()
    lr_metrics, lr_trained = train_and_log(
        lr_model, "LinearRegression",
        {"model": "LinearRegression"},
        X_train, X_test, y_train, y_test,
        dataset_name
    )
    results["LinearRegression"]        = lr_metrics
    trained_models["LinearRegression"] = lr_trained

    # ── 2. Random Forest ──────────────────────────────────────────────────
    rf_params = params["random_forest"]
    rf_model  = RandomForestRegressor(**rf_params)
    rf_metrics, rf_trained = train_and_log(
        rf_model, "RandomForest",
        rf_params,
        X_train, X_test, y_train, y_test,
        dataset_name
    )
    results["RandomForest"]        = rf_metrics
    trained_models["RandomForest"] = rf_trained

    # ── 3. XGBoost ────────────────────────────────────────────────────────
    xgb_params = params["xgboost"]
    xgb_model  = XGBRegressor(**xgb_params, verbosity=0)
    xgb_metrics, xgb_trained = train_and_log(
        xgb_model, "XGBoost",
        xgb_params,
        X_train, X_test, y_train, y_test,
        dataset_name
    )
    results["XGBoost"]        = xgb_metrics
    trained_models["XGBoost"] = xgb_trained

    # ── Sélectionner le meilleur modèle (RMSE minimal) ────────────────────
    best_name  = min(results, key=lambda m: results[m]["rmse"])
    best_model = trained_models[best_name]

    print(f"\n🏆 Meilleur modèle [{dataset_name}]: {best_name} "
          f"(RMSE={results[best_name]['rmse']:.4f})")

    # ── Sauvegarder le meilleur modèle ────────────────────────────────────
    models_dir = f"models/{dataset_name}"
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(best_model, f"{models_dir}/best_model.pkl")

    # ── Sauvegarder les métriques pour evaluate.py ────────────────────────
    os.makedirs("reports", exist_ok=True)
    results["best_model"] = best_name
    metrics_path = f"reports/metrics_{dataset_name}.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Modèle sauvegardé   : {models_dir}/best_model.pkl")
    print(f"✅ Métriques sauvegardées : {metrics_path}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    params = load_params()

    all_results = {}

    for dataset_name in ["arbres", "masse"]:
        all_results[dataset_name] = train_dataset(dataset_name, params)

    # ── Résumé global des 6 modèles ───────────────────────────────────────
    print(f"\n{'='*55}")
    print("  RÉSUMÉ GLOBAL")
    print(f"{'='*55}")

    for dataset_name, results in all_results.items():
        target = params[dataset_name]["target"]
        print(f"\n  [{dataset_name.upper()}]  target={target}  |  "
              f"Meilleur: {results['best_model']}")
        for model in ["LinearRegression", "RandomForest", "XGBoost"]:
            m    = results[model]
            flag = " 🏆" if model == results["best_model"] else ""
            print(f"    {model:<22} MAE={m['mae']:>12.4f}  "
                  f"RMSE={m['rmse']:>12.4f}  R²={m['r2']:>6.4f}{flag}")


if __name__ == "__main__":
    main()