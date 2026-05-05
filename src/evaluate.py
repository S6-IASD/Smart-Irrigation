"""
evaluate.py
-----------
Rôle : Générer des visualisations et un rapport de comparaison des modèles
Communication : Consomme reports/metrics_{dataset}.json → Produit reports/figures/
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import joblib
import os


def plot_model_comparison(metrics, dataset_name, target_label):
    """Graphe de comparaison des 3 modèles"""
    models    = [k for k in metrics.keys() if k != "best_model"]
    mae_vals  = [metrics[m]["mae"]  for m in models]
    rmse_vals = [metrics[m]["rmse"] for m in models]
    r2_vals   = [metrics[m]["r2"]   for m in models]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ["#3498db", "#2ecc71", "#e74c3c"]

    for ax, vals, title, ylabel in zip(
        axes,
        [mae_vals, rmse_vals, r2_vals],
        [f"MAE (↓ better) [{target_label}]",
         f"RMSE (↓ better) [{target_label}]",
         "R² Score (↑ better)"],
        ["MAE", "RMSE", "R²"]
    ):
        bars = ax.bar(models, vals, color=colors, edgecolor="black", linewidth=0.8)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, max(vals) * 1.2)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.01,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    best = metrics.get("best_model", "")
    plt.suptitle(
        f"Model Comparison – {dataset_name.upper()} (target: {target_label})\nBest: {best}",
        fontsize=14, fontweight="bold"
    )
    plt.tight_layout()

    out_path = f"reports/figures/model_comparison_{dataset_name}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Graphe sauvegardé: {out_path}")


def plot_feature_importance(model_path, feature_names, dataset_name):
    """Feature importance pour RF ou XGBoost"""
    model = joblib.load(model_path)

    if not hasattr(model, "feature_importances_"):
        print(f"ℹ️  [{dataset_name}] Pas de feature importance (Linear Regression)")
        return

    importances = model.feature_importances_
    indices     = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(importances)),
            importances[indices],
            color="#2ecc71", edgecolor="black")
    plt.xticks(range(len(importances)),
               [feature_names[i] for i in indices],
               rotation=45, ha="right")
    plt.title(f"Feature Importance – {dataset_name.upper()} (Best Model)",
              fontsize=13, fontweight="bold")
    plt.ylabel("Importance")
    plt.tight_layout()

    out_path = f"reports/figures/feature_importance_{dataset_name}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Graphe sauvegardé: {out_path}")


def print_summary(metrics, dataset_name, target_label):
    """Résumé console pour un dataset"""
    print(f"\n  [{dataset_name.upper()}]  target: {target_label}"
          f"  |  Meilleur: {metrics['best_model']}")
    for model, m in metrics.items():
        if model == "best_model":
            continue
        flag = " 🏆" if model == metrics["best_model"] else ""
        print(f"    {model}:{flag}")
        print(f"      MAE:  {m['mae']:.4f}")
        print(f"      RMSE: {m['rmse']:.4f}")
        print(f"      R²:   {m['r2']:.4f}")
        print(f"      MAPE: {m['mape']:.2f}%")


def main():
    os.makedirs("reports/figures", exist_ok=True)

    # Mapping dataset → label de la target (pour les titres)
    targets = {
        "arbres": "eau_mm",
        "masse":  "eau_litres",
    }

    print("📊 Génération des visualisations...")

    for dataset_name, target_label in targets.items():

        # ── Chargement des métriques ──────────────────────────────────────
        metrics_path = f"reports/metrics_{dataset_name}.json"
        with open(metrics_path, "r") as f:
            metrics = json.load(f)

        # ── Comparaison des modèles ───────────────────────────────────────
        plot_model_comparison(metrics, dataset_name, target_label)

        # ── Feature importance du meilleur modèle ─────────────────────────
        model_path = f"models/{dataset_name}/best_model.pkl"
        X_train    = pd.read_csv(f"data/processed/{dataset_name}/X_train.csv")
        plot_feature_importance(model_path, list(X_train.columns), dataset_name)

    # ── Résumé console global ─────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 50)

    for dataset_name, target_label in targets.items():
        with open(f"reports/metrics_{dataset_name}.json", "r") as f:
            metrics = json.load(f)
        print_summary(metrics, dataset_name, target_label)


if __name__ == "__main__":
    main()