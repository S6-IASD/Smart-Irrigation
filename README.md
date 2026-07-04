# 🌱 Smart Irrigation — Plateforme MLOps d'irrigation intelligente

Prédiction des besoins en eau d'irrigation par Machine Learning, du capteur IoT jusqu'au tableau de bord web, avec un pipeline de données et de modèles entièrement versionné et automatisé.

Le projet couvre 4 pôles complémentaires : **DataOps**, **MLOps**, **Développement applicatif (Backend/Frontend)** et **DevOps**.

---

## 📌 Vue d'ensemble

Le système collecte des données météo, agronomiques et de capteurs de sol pour deux familles de cultures — **arbres fruitiers** et **cultures en masse** — puis entraîne des modèles de régression capables d'estimer le volume d'eau à apporter. Le résultat est exposé via une API Django REST et une interface web React, avec ingestion possible de données IoT en temps réel.

```
Capteurs IoT / Météo
        │
        ▼
   ┌──────────┐      ┌──────────┐      ┌──────────────────┐      ┌──────────────┐
   │ DataOps  │ ───▶ │  MLOps   │ ───▶ │ Backend (Django)  │ ───▶ │ Frontend      │
   │ collecte │      │ DVC +    │      │ API REST + modèle │      │ (React/Vite)  │
   │ nettoyage│      │ MLflow   │      │ + PostgreSQL      │      │ Dashboard     │
   └──────────┘      └──────────┘      └──────────────────┘      └──────────────┘
                                                 ▲
                                                 │
                                     ┌───────────────────────┐
                                     │        DevOps          │
                                     │ Docker · Compose · CI  │
                                     │ GitHub Actions · Railway│
                                     └───────────────────────┘
```

---

## 🗂️ Structure du dépôt

```
Smart-Irrigation/
├── dataops/                  # Collecte, nettoyage, EDA, feature engineering
│   ├── data/
│   └── scripts/
│       ├── phase1_collecte.py
│       ├── phase2_nettoyage.py
│       ├── phase3_eda.py
│       ├── phase4_features.py
│       └── phase5_split.py
│
├── src/                       # Pipeline MLOps (DVC)
│   ├── data_ingestion.py
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
├── models/                    # Modèles entraînés (arbres/, masse/) — trackés en partie via Git/DVC
├── dvc.yaml / dvc.lock        # Définition et snapshot du pipeline DVC
├── params.yaml                # Hyperparamètres centralisés
├── mlflow.db                  # Base de tracking MLflow (SQLite)
├── simulateur_iot.py          # Simulateur de capteur IoT (envoi HTTP vers l'API)
│
├── backend/                   # API Django REST + PostgreSQL
│   ├── users/                 # Authentification JWT
│   ├── parcelles/             # Gestion des parcelles agricoles
│   ├── capteurs/              # Ingestion des données de capteurs (IoT)
│   ├── meteo/                 # Intégration données météo
│   ├── prediction/            # Endpoint de prédiction + scheduler
│   ├── models/                # Modèles ML embarqués côté API (arbres/, masse/)
│   ├── tests/                 # Suite pytest (auth, capteurs, météo, parcelles, prédiction)
│   ├── Dockerfile
│   └── docker-compose.yml     # Stack backend seule (dev local)
│
├── front-end/                  # Application React (Vite)
│   ├── src/
│   │   ├── pages/              # Dashboard, Parcelles, Historique, Admin*, Login, Register…
│   │   ├── components/         # Sidebar, PrivateRoute, LoadingSpinner
│   │   ├── context/             # AuthContext
│   │   └── api/                # Client Axios
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml          # Stack complète (db + backend + frontend)
└── .github/workflows/
    └── backend-ci.yml          # Pipeline CI (tests + build image Docker)
```

---

## 1️⃣ DataOps — Préparation des données

*Branche : `dataops` — contact : o.boulaarab5287@uca.ac.ma*

| Phase | Script | Résultat |
|---|---|---|
| Phase 1 — Collecte | `phase1_collecte.py` | `data_raw.csv` |
| Phase 2 — Nettoyage | `phase2_nettoyage.py` | `data_clean.csv` |
| Phase 3 — Analyse exploratoire | `phase3_eda.py` | `distributions.png` + `correlations.png` |
| Phase 4 — Feature engineering | `phase4_features.py` | `data_features.csv` |
| Phase 5 — Séparation | `phase5_split.py` | `data_arbres.csv` + `data_masse.csv` |

**Livrables pour l'équipe MLOps** (`dataops/data/processed/`) :

- **`data_arbres.csv`** — Oranger, Citronnier, Olivier… → target `eau_mm`
- **`data_masse.csv`** — Blé, Maïs, Tomate… → target `eau_litres`

### Colonnes principales du dataset

| Colonne | Description |
|---|---|
| `date`, `ville`, `latitude`/`longitude` | Contexte temporel et géographique |
| `T_min` / `T_max`, `pluie_mm`, `vent_kmh`, `ensoleillement_h` | Variables météo |
| `humidite_sol`, `temperature_sol`, `N`/`P`/`K` | Variables agronomiques (sol) |
| `type_plante`, `stade`, `kc`, `ET0`, `superficie_ha` | Variables culture |
| `saison`, `fertilite_sol`, `type_culture` | Features générées en Phase 4 |
| `eau_litres` / `eau_mm` | Cibles (masse / arbres) |

> Les données livrées sont propres et prêtes à l'entraînement ; encodage et normalisation restent à la charge de l'équipe MLOps.

---

## 2️⃣ MLOps — Entraînement, tracking et reproductibilité

*Branche : `mlops` — contact : s.elangui0874@uca.ac.ma*

### Modèles comparés

| # | Modèle | Rôle |
|---|---|---|
| 1 | Linear Regression | Baseline, rapide et interprétable |
| 2 | Random Forest Regressor | Robuste aux outliers, pas de scaling requis |
| 3 | XGBoost Regressor | Gradient boosting, généralement le plus performant |

Le meilleur modèle est sélectionné automatiquement selon le **RMSE minimal**, séparément pour les datasets `arbres` et `masse`.

### Métriques suivies
MAE, RMSE, R², MAPE — loguées et versionnées à chaque run.

### Pipeline DVC (`dvc.yaml`)

4 stages chaînés, chacun ne se relance que si ses dépendances changent :

```
data_ingestion → preprocess → train → evaluate
```

| Stage | Commande | Sorties principales |
|---|---|---|
| `data_ingestion` | `python src/data_ingestion.py` | `data/raw/data_arbres.csv`, `data/raw/data_masse.csv` |
| `preprocess` | `python src/preprocess.py` | splits train/test + `scaler.pkl` + `encoders.pkl` par dataset |
| `train` | `python src/train.py` | `best_model.pkl` + métriques JSON (MLflow) |
| `evaluate` | `python src/evaluate.py` | figures de comparaison dans `reports/figures/` |

```bash
pip install -r requirements.txt
dvc repro                 # lance tout le pipeline (ou uniquement ce qui a changé)
dvc repro --force         # relance complète
dvc repro preprocess      # relance un seul stage
dvc status                # stages obsolètes ?
dvc dag                   # graphe de dépendances
dvc metrics show          # métriques du run courant
dvc metrics diff HEAD~1   # comparaison entre runs
```

### Tracking MLflow

```bash
mlflow ui
# → http://localhost:5000
```
Deux expériences distinctes : `smart_irrigation_arbres` et `smart_irrigation_masse` (paramètres, métriques, artefacts modèle, historique).

### Prédiction manuelle

```python
from predict import predict

result = predict(
    input_data={
        "T_min": 18.0, "T_max": 38.0,
        "humidite_sol": 35.0, "temperature_sol": 28.0,
        "N": 1.2, "P": 0.8, "K": 1.5, "pluie_mm": 0.0,
        "type_plante": "Oranger", "stade": "mature",
    },
    dataset="arbres"
)
print(f"Besoin en eau : {result:.4f} mm/jour")
```

### Ce que Git versionne vs ce que DVC versionne

| Fichier | Versionné par |
|---|---|
| `dvc.yaml`, `dvc.lock`, `params.yaml`, `src/*.py` | Git |
| `data/raw/*.csv`, `data/processed/**`, `models/**/*.pkl` | DVC |
| `reports/metrics_*.json` | Git (`cache: false`) |
| `reports/figures/*.png` | DVC |

---

## 3️⃣ Application — Backend & Frontend

### Backend — API Django REST

Applications Django modulaires :

| App | Rôle |
|---|---|
| `users` | Authentification JWT (inscription, connexion, rôles) |
| `parcelles` | CRUD des parcelles agricoles (localisation, culture, superficie) |
| `capteurs` | Ingestion des lectures de capteurs (humidité, température, NPK) — endpoint `/api/iot/ingest/` sécurisé par clé API |
| `meteo` | Récupération et exposition des données météo |
| `prediction` | Endpoint de prédiction (chargement des modèles `.pkl`) + `scheduler.py` (tâches planifiées via `django-apscheduler`) |

**Stack technique :** Django 4.2, Django REST Framework, SimpleJWT, PostgreSQL, Gunicorn, WhiteNoise, scikit-learn/XGBoost pour l'inférence.

**Routes principales (`config/urls.py`) :**
```
/api/auth/          → users
/api/parcelles/      → parcelles
/api/                → capteurs (capteurs, lectures)
/api/meteo/           → meteo
/api/prediction/      → prediction
/admin/               → interface d'administration Django
```

**Tests :** suite `pytest` couvrant auth, capteurs, météo, parcelles et prédiction (`backend/tests/`, exécutée aussi par app dans `parcelles/tests.py`, `prediction/tests.py`, `users/tests.py`).

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
pytest tests/ -v --cov=.
python manage.py runserver
```

### Simulateur IoT

`simulateur_iot.py` simule un capteur (type ESP32) envoyant des mesures de sol (humidité, température, NPK) en HTTP vers `/api/iot/ingest/`, authentifié par clé API — utile pour tester le pipeline d'ingestion sans matériel physique.

```bash
python simulateur_iot.py --device-id capteur_01 --api-key <clé> --server-url http://localhost:8000
```

### Frontend — React (Vite)

**Stack technique :** React 19, Vite, React Router, Axios, Bootstrap / React-Bootstrap, Leaflet / React-Leaflet (cartographie des parcelles), Recharts (visualisation), React-Toastify.

**Pages principales :**
- `Home`, `Login`, `Register`
- `Dashboard`, `Historique`, `Parcelles`, `ParcelleDetail`
- Espace admin : `AdminDashboard`, `AdminParcelles`, `AdminCapteurs`, `AdminUsers`
- `PrivateRoute` + `AuthContext` pour la gestion des sessions authentifiées

```bash
cd front-end
npm install
npm run dev        # développement (Vite)
npm run build       # build de production
npm run lint
```

---

## 4️⃣ DevOps — Conteneurisation, orchestration & CI/CD

*Cette section documente et complète l'automatisation déjà en place dans le dépôt.*

### Conteneurisation

Chaque composant dispose de son propre `Dockerfile` :

- **`backend/Dockerfile`** — image `python:3.11-slim`, dépendances système pour `psycopg2` (`libpq-dev`, `gcc`), installation des requirements, puis au démarrage : migrations Django → `collectstatic` → serveur **Gunicorn** (`config.wsgi:application`, 2-3 workers).
- **`front-end/Dockerfile`** — build **multi-stage** : étape 1 (`node:20-alpine`) compile l'app Vite (variable `VITE_API_URL` injectée au build) ; étape 2 (`nginx:alpine`) sert les fichiers statiques buildés avec une configuration Nginx dédiée (`nginx.conf` : SPA fallback vers `index.html`, cache long sur assets statiques `.css/.js/.png/...`).

### Orchestration — Docker Compose

Deux niveaux de composition :

1. **`docker-compose.yml` (racine)** — stack complète prête pour un déploiement local/staging :
   - `db` : PostgreSQL 15-alpine, volume persistant, healthcheck `pg_isready`
   - `backend` : build depuis `./backend`, dépend de `db` (attend qu'il soit *healthy*), migrations + collectstatic + Gunicorn au démarrage, healthcheck via `manage.py check --deploy`
   - `frontend` : build depuis `./front-end`, servi par Nginx sur le port 80, dépend de `backend`
   - Réseau dédié `smart_network` (bridge) et volumes nommés (`postgres_data`, `static_volume`)

2. **`backend/docker-compose.yml`** — stack allégée pour le développement isolé du backend (DB + API uniquement, `DEBUG=True`), pratique pour itérer sans reconstruire le frontend.

```bash
# Lancer toute la plateforme
docker compose up --build

# Lancer uniquement le backend en dev
cd backend && docker compose up --build
```

### Intégration continue — GitHub Actions

Workflow `.github/workflows/backend-ci.yml`, déclenché sur chaque `push`/`pull_request` vers `main` :

| Job | Détail |
|---|---|
| **`pytest`** | Service `postgres:15` éphémère → installation des dépendances → `manage.py migrate` → `pytest tests/ -v --cov=. --cov-report=xml` → upload de la couverture vers **Codecov** |
| **`docker-build`** | *(dépend du succès de `pytest`)* build de l'image `smart-irrigation-backend` pour valider que le `Dockerfile` est sain avant merge |

Ce pipeline garantit qu'aucun code cassé (tests en échec) ou image non-buildable n'atteint la branche principale.

### Déploiement en production

Le projet est déployé selon une architecture **cloud multi-services**, chaque composant étant hébergé sur la plateforme la plus adaptée :

| Composant | Plateforme | Détail |
|---|---|---|
| **Base de données** | **Supabase** (PostgreSQL managé) | Remplace le conteneur `db` local en production |
| **Backend (API Django)** | **Railway** | Build à partir de `backend/Dockerfile`, connecté à la base Supabase via variables d'environnement ; modèles ML (`.pkl`) packagés avec l'image pour l'inférence (cf. historique des commits « Fix model path for Railway deployment ») |
| **Frontend (React)** | **Vercel** | Build Vite déployé directement (hors conteneur Nginx, qui reste utile pour un déploiement Docker autonome) ; `VITE_API_URL` pointe vers l'API Railway |

En local/dev, le `docker-compose.yml` à la racine reste la référence pour lancer la stack complète (DB + backend + frontend conteneurisés) sans dépendre des services cloud.

### Axes d'amélioration DevOps proposés *(non encore présents dans le dépôt — suggestions)*

Ces éléments n'existent pas encore dans le code observé ; ils sont proposés pour compléter la chaîne DevOps :

- **CI Frontend** : ajouter un job GitHub Actions dédié (`lint` + `build` Vite), en miroir de `backend-ci.yml`, avant que Vercel ne déploie automatiquement sur push.
- **CD automatisé pour le backend** : Railway peut être branché directement sur `main` (auto-deploy au push) ou déclenché via Railway CLI/webhook en fin de pipeline GitHub Actions, une fois `pytest` + `docker-build` validés.
- **Gestion des secrets** : `SECRET_KEY`, URL/clé Supabase, clés API IoT sont à définir comme variables d'environnement chiffrées dans Railway / Vercel / GitHub Actions Secrets — jamais en clair comme dans le `docker-compose.yml` local (usage dev uniquement).
- **Registry d'images** : publier l'image `smart-irrigation-backend` buildée en CI sur un registre (GHCR/Docker Hub) taggée par commit SHA, que Railway peut ensuite consommer (déploiement par image plutôt que rebuild).
- **Environnements séparés** : environnements Railway/Vercel distincts (preview/staging/production) avec bases Supabase séparées, pour tester une PR sans impacter la prod.
- **Monitoring** : exposer un endpoint `/health/` côté API pour les healthchecks Railway, et suivre les logs Supabase/Railway/Vercel de manière centralisée.
- **Scan de sécurité** : job CI de scan de l'image Docker (ex. Trivy) et audit des dépendances (`pip-audit`, `npm audit`).

---

## 🚀 Démarrage rapide (stack complète)

```bash
# 1. Cloner le dépôt
git clone https://github.com/S6-IASD/Smart-Irrigation.git
cd Smart-Irrigation

# 2. Lancer la stack applicative (DB + API + Frontend)
docker compose up --build
# API      → http://localhost:8000
# Frontend → http://localhost:80

# 3. (Optionnel) Reproduire le pipeline ML
pip install -r requirements.txt
dvc repro
mlflow ui   # http://localhost:5000
```

---

## 👥 Organisation des équipes

| Pôle | Branche | Contact |
|---|---|---|
| DataOps | `dataops` | o.boulaarab5287@uca.ac.ma |
| MLOps | `mlops` | s.elangui0874@uca.ac.ma |
| Backend / Frontend / DevOps | `backend-initialisation` | bousebbatk@gmail.com — CI/CD (GitHub Actions), conteneurisation (Docker/Docker Compose) et déploiement cloud (Supabase, Railway, Vercel) |

---

## 🧩 Stack technique — résumé

| Domaine | Outils |
|---|---|
| Data & ML | pandas, numpy, scikit-learn, XGBoost, DVC, MLflow, joblib |
| Backend | Django, Django REST Framework, SimpleJWT, PostgreSQL, Gunicorn, WhiteNoise, django-apscheduler |
| Frontend | React 19, Vite, React Router, Axios, Bootstrap, Leaflet, Recharts |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions, Codecov, Supabase (DB), Railway (backend), Vercel (frontend) |
