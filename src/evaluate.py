"""
evaluate.py
-----------
Rôle : Générer des visualisations et un rapport de comparaison des modèles
Communication : Consomme reports/metrics.json → Produit reports/figures/
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import joblib
import os

def plot_model_comparison(metrics):
    """Graphe de comparaison des 3 modèles"""
    models = [k for k in metrics.keys() if k != "best_model"]
    mae_vals  = [metrics[m]["mae"]  for m in models]
    rmse_vals = [metrics[m]["rmse"] for m in models]
    r2_vals   = [metrics[m]["r2"]   for m in models]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ["#3498db", "#2ecc71", "#e74c3c"]
    
    for ax, vals, title, ylabel in zip(
        axes,
        [mae_vals, rmse_vals, r2_vals],
        ["MAE (↓ better)", "RMSE (↓ better)", "R² Score (↑ better)"],
        ["MAE", "RMSE", "R²"]
    ):
        bars = ax.bar(models, vals, color=colors, edgecolor="black", linewidth=0.8)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, max(vals) * 1.2)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    
    best = metrics.get("best_model", "")
    plt.suptitle(f"Model Comparison – Water Need Prediction\n🏆 Best: {best}",
                fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("reports/figures/model_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Graphe sauvegardé: reports/figures/model_comparison.png")

def plot_feature_importance(model_path, feature_names):
    """Feature importance pour RF ou XGBoost"""
    model = joblib.load(model_path)
    
    if not hasattr(model, "feature_importances_"):
        print("ℹ️ Pas de feature importance pour ce modèle (Linear Regression)")
        return
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(importances)),
            importances[indices],
            color="#2ecc71", edgecolor="black")
    plt.xticks(range(len(importances)),
               [feature_names[i] for i in indices], rotation=45, ha="right")
    plt.title("Feature Importance – Best Model", fontsize=13, fontweight="bold")
    plt.ylabel("Importance")
    plt.tight_layout()
    plt.savefig("reports/figures/feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Graphe sauvegardé: reports/figures/feature_importance.png")

def main():
    os.makedirs("reports/figures", exist_ok=True)
    
    with open("reports/metrics.json", "r") as f:
        metrics = json.load(f)
    
    print("📊 Génération des visualisations...")
    plot_model_comparison(metrics)
    
    # Feature importance
    X_train = pd.read_csv("data/processed/X_train.csv")
    plot_feature_importance("models/best_model.pkl", list(X_train.columns))
    
    # Résumé console
    print("\n" + "="*50)
    print("📋 RÉSUMÉ FINAL")
    print("="*50)
    for model, m in metrics.items():
        if model == "best_model":
            print(f"\n Meilleur modèle: {m}")
            continue
        print(f"\n{model}:")
        print(f"  MAE:  {m['mae']:.4f} mm/jour")
        print(f"  RMSE: {m['rmse']:.4f} mm/jour")
        print(f"  R²:   {m['r2']:.4f}")
        print(f"  MAPE: {m['mape']:.2f}%")

if __name__ == "__main__":
    main()