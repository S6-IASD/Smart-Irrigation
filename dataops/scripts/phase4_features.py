import pandas as pd

df = pd.read_csv("data/processed/data_clean.csv")
df["date"] = pd.to_datetime(df["date"])

# Saison
def get_saison(mois):
    if mois in [12, 1, 2]:   return "hiver"
    elif mois in [3, 4, 5]:  return "printemps"
    elif mois in [6, 7, 8]:  return "ete"
    else:                     return "automne"

df["saison"] = df["mois"].apply(get_saison)

# Stress hydrique (logique naturelle)
df["stress_hydrique"] = (df["eau_mm"] > 0).astype(int)
print(f"  Stress=0 (pas d'irrigation) : {(df['stress_hydrique']==0).sum()} lignes")
print(f"  Stress=1 (irrigation needed) : {(df['stress_hydrique']==1).sum()} lignes")

# Amplitude thermique
df["amplitude_thermique"] = (df["T_max"] - df["T_min"]).round(2)

# Richesse du sol
df["fertilite_sol"] = df["N"] + df["P"] + df["K"]

df.to_csv("data/processed/data_features.csv", index=False)
print(f"\n✅ data_features.csv sauvegardé : {df.shape[0]} lignes × {df.shape[1]} colonnes")