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

