"""
train.py
--------
Rôle : Entraîner les 3 modèles et logger TOUT dans MLflow
Communication : Consomme data/processed/ → Produit models/best_model.pkl
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
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def compute_metrics(y_true, y_pred, model_name):
    """Calcule toutes les métriques"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape_val = mape(y_true, y_pred)
    
    print(f"\n📊 {model_name}:")
    print(f"   MAE:  {mae:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R²:   {r2:.4f}")
    print(f"   MAPE: {mape_val:.2f}%")
    
    return {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape_val}

def train_and_log(model, model_name, params_to_log, X_train, X_test, y_train, y_test):
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
        
        # Tag pour identifier facilement
        mlflow.set_tag("model_type", model_name)
        mlflow.set_tag("dataset", "soil_water")
        
        run_id = mlflow.active_run().info.run_id
        print(f"   MLflow run_id: {run_id}")
    
    return metrics, model

def main():
    params = load_params()
    
    # Charger données
    X_train = pd.read_csv("data/processed/X_train.csv")
    X_test  = pd.read_csv("data/processed/X_test.csv")
    y_train = pd.read_csv("data/processed/y_train.csv").squeeze()
    y_test  = pd.read_csv("data/processed/y_test.csv").squeeze()
    
    print(f"📂 Données chargées: Train={X_train.shape}, Test={X_test.shape}")
    
    # ✅ MLflow Experiment
    mlflow.set_experiment("water_need_prediction")
    
    results = {}
    
    # ── 1. BASELINE : Linear Regression ──────────────────────────────────
    lr_model = LinearRegression()
    lr_metrics, lr_trained = train_and_log(
        lr_model, "LinearRegression",
        {"model": "LinearRegression"},
        X_train, X_test, y_train, y_test
    )
    results["LinearRegression"] = lr_metrics
    
    # ── 2. Random Forest ──────────────────────────────────────────────────
    rf_params = params["random_forest"]
    rf_model = RandomForestRegressor(**rf_params)
    rf_metrics, rf_trained = train_and_log(
        rf_model, "RandomForest",
        rf_params,
        X_train, X_test, y_train, y_test
    )
    results["RandomForest"] = rf_metrics
    
    # ── 3. XGBoost ────────────────────────────────────────────────────────
    xgb_params = params["xgboost"]
    xgb_model = XGBRegressor(**xgb_params, verbosity=0)
    xgb_metrics, xgb_trained = train_and_log(
        xgb_model, "XGBoost",
        xgb_params,
        X_train, X_test, y_train, y_test
    )
    results["XGBoost"] = xgb_metrics
    
    # ── Choisir le meilleur modèle (RMSE le plus bas) ─────────────────────
    best_name = min(results, key=lambda m: results[m]["rmse"])
    best_models = {
        "LinearRegression": lr_trained,
        "RandomForest": rf_trained,
        "XGBoost": xgb_trained
    }
    best_model = best_models[best_name]
    
    print(f"\n🏆 Meilleur modèle: {best_name} (RMSE={results[best_name]['rmse']:.4f})")
    
    # Sauvegarder le meilleur
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/best_model.pkl")
    
    # Sauvegarder les résultats pour evaluate.py
    results["best_model"] = best_name
    os.makedirs("reports", exist_ok=True)
    with open("reports/metrics.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Modèle sauvegardé: models/best_model.pkl")
    print(f"✅ Métriques sauvegardées: reports/metrics.json")

if __name__ == "__main__":
    main()