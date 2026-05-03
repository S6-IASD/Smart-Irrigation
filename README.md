# 🌱 Smart Irrigation – MLOps Project

## 📌 Project Overview
This project aims to predict soil water needs using a complete MLOps pipeline.  
It integrates **DVC for data/version control** and **MLflow for experiment tracking**, ensuring reproducibility and experiment management.

The system compares multiple machine learning models and selects the best-performing one based on evaluation metrics.

---

## 🎯 Objective
- Predict water needs in soil (regression problem)
- Compare multiple ML models
- Build a reproducible MLOps pipeline
- Track experiments and models properly

---

## 🧠 Machine Learning Models Used
- Linear Regression (Baseline model)
- Random Forest Regressor
- XGBoost Regressor

---

## 📊 Evaluation Metrics
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score
- MAPE (Mean Absolute Percentage Error)

---

## 🏗️ Project Architecture
project/
│── data/
│ ├── raw/
│ ├── processed/
│
│── src/
│ ├── data_ingestion.py
│ ├── preprocess.py
│ ├── train.py
│ ├── evaluate.py
│ ├── predict.py
│
│── models/
│── reports/
│── dvc.yaml
│── params.yaml
│── requirements.txt

---

## ⚙️ Pipeline Flow (DVC)
data_ingestion → preprocess → train → evaluate

Each stage is automatically executed using:

```bash
dvc repro
🔬 MLflow Tracking

MLflow is used to track:

Model parameters
Evaluation metrics
Trained models
Experiment history

Run MLflow UI:
mlflow ui
Then open:

http://localhost:5000

1. Install dependencies
pip install -r requirements.txt
2. Initialize DVC (if needed)
dvc init
3. Run full pipeline
dvc repro
4. Launch MLflow
mlflow ui

# DataOps — Smart-Irrigation

Ce dépôt couvre la partie **préparation des données** du projet Smart-Irrigation.

---

## Ce que l'équipe DataOps fait

| Phase | Script | Résultat |  
|-------|--------|----------|  
| Phase 1 — Collection | `phase1_collecte.py` | `data_raw.csv` |  
| Phase 2 — Nettoyage | `phase2_clean.py` | `data_clean.csv` |  
| Phase 3 — Analyse Exploratoire | `phase3_eda.py` | `distributions.png` + `correlations.png` |  
| Phase 4 — Feature Engineering | `phase4_features.py` | `data_features.csv` |  
| Phase 5 — Séparation | `phase5_split.py` | `data_arbres.csv` + `data_masse.csv` |  

---

## Ce que l'équipe MLOps reçois

Deux fichiers dans `data/processed/`, prêts à l'entraînement :

**`data_arbres.csv`** — Oranger, Citronnier, Olivier…
- Target : `eau_mm`

**`data_masse.csv`** — Blé, Maïs, Tomate…
- Target : `eau_litres`

---

### Colonnes du dataset

| Colonne | Description |  
|---------|-------------|  
| `date` | Date de l'observation |  
| `ville` | Localisation |  
| `latitude` / `longitude` | Coordonnées GPS |  
| `T_min` / `T_max` | Température min/max (°C) |  
| `pluie_mm` | Précipitations (mm) |  
| `vent_kmh` | Vitesse du vent (km/h) |  
| `ensoleillement_h` | Heures d'ensoleillement |  
| `mois` | Mois de l'observation |  
| `type_plante` | Espèce végétale |  
| `stade` | Stade phénologique (jeune / mature / fin) |  
| `humidite_sol` | Humidité du sol (%) |  
| `temperature_sol` | Température du sol (°C) |  
| `N` / `P` / `K` | Nutriments du sol (kg/ha) |  
| `kc` | Coefficient cultural |  
| `ET0` | Évapotranspiration de référence |  
| `superficie_ha` | Surface de la parcelle (ha) |  
| `eau_litres` | Volume d'eau total (litres) — **target masse** |  
| `eau_mm` | Lame d'eau (mm) — **target arbres** |  
| `saison` | ✨ Générée — printemps / été / automne / hiver |  
| `fertilite_sol` | ✨ Générée — score NPK normalisé |  
| `type_culture` | ✨ Générée — `arbre` ou `masse` |  

> ✨ = features construites en Phase 3 (feature engineering).  
> Les données sont propres et prêtes à l'entraînement. L'encodage et la normalisation sont à la charge de l'équipe MLOps.

---

*Branche : `dataops` — contact : o.boulaarab5287@uca.ac.ma*




# 🌿 Smart Irrigation – Pipeline MLOps

Projet de prédiction des besoins en eau d'irrigation par machine learning.  
Deux datasets sont traités en parallèle : **arbres fruitiers** et **cultures en masse**.

---

## 📁 Structure du projet

```
Smart-Irrigation/
│
├── data/
│   ├── raw/                        # CSV copiés depuis le DataOps
│   │   ├── data_arbres.csv
│   │   └── data_masse.csv
│   └── processed/                  # Splits train/test après preprocessing
│       ├── arbres/
│       │   ├── X_train.csv
│       │   ├── X_test.csv
│       │   ├── y_train.csv
│       │   └── y_test.csv
│       └── masse/
│           ├── X_train.csv
│           ├── X_test.csv
│           ├── y_train.csv
│           └── y_test.csv
│
├── models/
│   ├── arbres/
│   │   ├── best_model.pkl          # Meilleur modèle sélectionné
│   │   ├── scaler.pkl              # Scaler fitté sur le train
│   │   └── encoders.pkl            # LabelEncoders (type_plante, stade)
│   └── masse/
│       ├── best_model.pkl
│       ├── scaler.pkl
│       └── encoders.pkl
│
├── reports/
│   ├── metrics_arbres.json         # MAE, RMSE, R², MAPE des 3 modèles
│   ├── metrics_masse.json
│   └── figures/
│       ├── model_comparison_arbres.png
│       ├── model_comparison_masse.png
│       ├── feature_importance_arbres.png
│       └── feature_importance_masse.png
│
├── data_ingestion.py               # Copie les datasets bruts vers data/raw/
├── preprocess.py                   # Encodage + scaling + split train/test
├── train.py                        # Entraînement 3 modèles + tracking MLflow
├── evaluate.py                     # Visualisations + rapport de comparaison
├── predict.py                      # Inférence sur nouvelles données
└── params.yaml                     # Configuration centralisée du pipeline
```

---

## 📊 Datasets

| Dataset | Source | Target | Lignes | Features clés |
|---|---|---|---|---|
| **arbres** | `dataops/data/processed/data_arbres.csv` | `eau_mm` | 18 929 | T_min, T_max, humidite_sol, N, P, K, pluie_mm, type_plante, stade |
| **masse** | `dataops/data/processed/data_masse.csv` | `eau_litres` | 42 462 | idem + `superficie_ha` |

**Cultures arbres :** Oranger, Citronnier, Olivier, Figuier, Noyer, Vigne, Dattier, Amandier, Grenadier  
**Cultures masse :** Tomate, Blé, Maïs, Laitue, Oignon, Betterave, Pomme de terre, Chou, Carotte, Orge, Tournesol, Ail, Colza

---

## 🧠 Modèles entraînés

3 modèles de régression sont entraînés et comparés pour chaque dataset :

| # | Modèle | Rôle |
|---|---|---|
| 1 | **Linear Regression** | Baseline – rapide, interprétable |
| 2 | **Random Forest** | Robuste aux valeurs aberrantes, pas de scaling requis |
| 3 | **XGBoost** | Gradient boosting, généralement le plus performant |

Le meilleur modèle est sélectionné automatiquement sur le critère **RMSE minimal**.

---

## ⚙️ Configuration – `params.yaml`

Tous les paramètres du pipeline sont centralisés dans `params.yaml` :

```yaml
preprocessing:
  scale_features: true
  scale_method: "standard"    # "standard" ou "minmax"

random_forest:
  n_estimators: 200
  max_depth: 15
  ...

xgboost:
  n_estimators: 300
  learning_rate: 0.05
  ...
```

Pour changer de scaler ou d'hyperparamètres : **modifier uniquement `params.yaml`**, aucun script à toucher.

---

## 🚀 Lancer le pipeline

### 1. Prérequis

```bash
pip install pandas numpy scikit-learn xgboost mlflow joblib pyyaml matplotlib
```

### 2. Pipeline complet – étape par étape

#### Étape 1 – Ingestion des données
```bash
python data_ingestion.py
```
Copie `data_arbres.csv` et `data_masse.csv` depuis le dossier DataOps vers `data/raw/`.

#### Étape 2 – Preprocessing
```bash
python preprocess.py
```
Pour chaque dataset :
- Sélection des features définies dans `params.yaml`
- Encodage LabelEncoder sur `type_plante` et `stade`
- Split train/test (80/20)
- Standardisation ou normalisation selon `scale_method`
- Sauvegarde dans `data/processed/{dataset}/`

#### Étape 3 – Entraînement
```bash
python train.py
```
Pour chaque dataset :
- Entraîne Linear Regression, Random Forest, XGBoost
- Logue paramètres + métriques + modèle dans **MLflow**
- Sélectionne le meilleur modèle (RMSE minimal)
- Sauvegarde dans `models/{dataset}/best_model.pkl`

#### Étape 4 – Évaluation
```bash
python evaluate.py
```
Génère les figures de comparaison dans `reports/figures/` et affiche le rapport final en console.

#### Étape 5 – Prédiction
```bash
python predict.py
```
Exemple de prédiction sur de nouvelles données pour les deux datasets.

---

### 3. Lancer tout le pipeline d'un coup

```bash
python data_ingestion.py && python preprocess.py && python train.py && python evaluate.py && python predict.py
```

---

### 4. Visualiser les expériences MLflow

```bash
mlflow ui
```
Ouvre **http://localhost:5000** dans ton navigateur.  
Tu trouveras deux expériences séparées :
- `smart_irrigation_arbres`
- `smart_irrigation_masse`

---

## 📈 Faire une prédiction manuelle

```python
from predict import predict

# Prédire le besoin en eau d'un oranger mature
result = predict(
    input_data={
        "T_min": 18.0,
        "T_max": 38.0,
        "humidite_sol": 35.0,
        "temperature_sol": 28.0,
        "N": 1.2, "P": 0.8, "K": 1.5,
        "pluie_mm": 0.0,
        "type_plante": "Oranger",
        "stade": "mature",
    },
    dataset="arbres"
)
print(f"Besoin en eau : {result:.4f} mm/jour")

# Prédire pour une culture de blé (5 ha)
result = predict(
    input_data={
        "T_min": 10.0,
        "T_max": 22.0,
        "humidite_sol": 45.0,
        "temperature_sol": 18.0,
        "N": 0.9, "P": 0.6, "K": 1.0,
        "pluie_mm": 5.0,
        "type_plante": "Blé",
        "stade": "jeune",
        "superficie_ha": 5.0,
    },
    dataset="masse"
)
print(f"Besoin en eau : {result:.2f} litres")
```

---

## 🔁 Flux du pipeline

```
DataOps (données nettoyées)
        ↓
data_ingestion.py   →   data/raw/
        ↓
preprocess.py       →   data/processed/  +  models/{dataset}/scaler.pkl
        ↓                                    models/{dataset}/encoders.pkl
train.py            →   models/{dataset}/best_model.pkl
        ↓                reports/metrics_{dataset}.json
evaluate.py         →   reports/figures/
        ↓
predict.py          →   prédiction en temps réel
```

---
# Section à intégrer dans ton README.md (branche mlops)
# Colle ce bloc AVANT ou APRÈS la section "🚀 Lancer le pipeline"

---

## 🔄 Pipeline reproductible avec DVC

> **DVC (Data Version Control)** est l'outil qui orchestre et versionne tout le pipeline MLOps.  
> Il joue le même rôle que `Makefile` mais pour le Machine Learning :  
> il sait **quoi relancer** et **quoi ignorer** selon ce qui a changé.

---

### Pourquoi DVC ?

| Sans DVC | Avec DVC |
|---|---|
| Tu relances tout le pipeline à la main | DVC détecte ce qui a changé et relance uniquement les étapes impactées |
| Les données ne sont pas versionnées | Chaque version des données est trackée comme un commit git |
| Impossible de reproduire une expérience passée | `dvc checkout` restaure données + modèles d'un commit précis |
| Les fichiers lourds (CSV, pkl) polluent git | DVC les stocke séparément, git ne garde que les pointeurs `.dvc` |

---

### Architecture du pipeline DVC (`dvc.yaml`)

Le pipeline est découpé en **4 stages chaînés**. DVC connaît les dépendances entre eux et ne relance que ce qui est nécessaire.

```
DataOps (données nettoyées)
        │
        ▼
┌─────────────────────┐
│  1. data_ingestion  │  cmd: python src/data_ingestion.py
│                     │  deps: data_arbres.csv, data_masse.csv (depuis DataOps)
│                     │  outs: data/raw/data_arbres.csv
│                     │        data/raw/data_masse.csv
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  2. preprocess      │  cmd: python src/preprocess.py
│                     │  deps: data/raw/*.csv + params.yaml
│                     │  outs: data/processed/arbres/  ← splits train/test
│                     │        data/processed/masse/
│                     │        models/arbres/scaler.pkl + encoders.pkl
│                     │        models/masse/scaler.pkl  + encoders.pkl
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  3. train           │  cmd: python src/train.py
│                     │  deps: data/processed/ + params.yaml
│                     │  outs: models/arbres/best_model.pkl
│                     │        models/masse/best_model.pkl
│                     │  metrics: reports/metrics_arbres.json
│                     │           reports/metrics_masse.json
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  4. evaluate        │  cmd: python src/evaluate.py
│                     │  deps: models/ + reports/metrics_*.json
│                     │  outs: reports/figures/*.png
└─────────────────────┘
```

---

### Lancer le pipeline avec DVC

#### ▶️ Lancer tout le pipeline (recommandé)
```bash
dvc repro
```
> DVC analyse les dépendances, détecte ce qui a changé (code, données, params) et **ne relance que les stages impactés**.

#### ▶️ Forcer la relance complète
```bash
dvc repro --force
```

#### ▶️ Lancer un seul stage
```bash
dvc repro preprocess   # relance uniquement le preprocessing
dvc repro train        # relance uniquement l'entraînement
```

#### ▶️ Voir le statut du pipeline
```bash
dvc status             # quels stages sont out-of-date ?
dvc dag                # affiche le graphe des dépendances
```

---

### Versionner une expérience

Après chaque `dvc repro`, commite les résultats :

```bash
# DVC met à jour dvc.lock (snapshot de tous les outputs)
git add dvc.lock reports/metrics_arbres.json reports/metrics_masse.json
git commit -m "exp: RandomForest n_estimators=200, RMSE arbres=0.42"
git tag -a "exp-rf-200" -m "Expérience RF 200 arbres"
```

Pour revenir à une expérience précédente :
```bash
git checkout exp-rf-200
dvc checkout            # restaure les données et modèles correspondants
```

---

### Comparer les métriques entre expériences

```bash
dvc metrics show                        # métriques du run actuel
dvc metrics diff HEAD~1                 # comparaison avec le run précédent
```

Exemple de sortie :
```
Path                        Metric    HEAD    HEAD~1    Change
reports/metrics_arbres.json rmse      0.42    0.51      -0.09 ✅
reports/metrics_masse.json  r2        0.89    0.84      +0.05 ✅
```

---

### Ce que DVC versionne vs Git

| Fichier | Versionné par |
|---|---|
| `dvc.yaml` (définition du pipeline) | **Git** |
| `dvc.lock` (snapshot des outputs) | **Git** |
| `params.yaml` (hyperparamètres) | **Git** |
| `src/*.py` (code) | **Git** |
| `data/raw/*.csv` | **DVC** (pointeur `.dvc` dans git) |
| `data/processed/**` | **DVC** |
| `models/**/*.pkl` | **DVC** |
| `reports/figures/*.png` | **DVC** |
| `reports/metrics_*.json` | **Git** (`cache: false`) |

---

### Prérequis supplémentaires

```bash
pip install dvc
```

> MLflow reste actif pendant `dvc repro` : chaque `train.py` logue automatiquement dans MLflow.  
> Tu peux donc comparer les expériences **à la fois** via `dvc metrics diff` et via `mlflow ui`.

## 👥 Architecture MLOps

| Composant | Outil |
|---|---|
| Tracking des expériences | MLflow |
| Versioning des paramètres | params.yaml |
| Sérialisation des modèles | joblib (.pkl) |
| Preprocessing reproductible | scikit-learn Pipeline (scaler + encoders sauvegardés) |
Branche : Mlops — contact : s.elangui0874@uca.ac.ma