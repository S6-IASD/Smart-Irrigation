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
| Phase 5 — Séparation | `phase4_split.py` | `data_arbres.csv` + `data_masse.csv` |  

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
