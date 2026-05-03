import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/processed/data_clean.csv")

# Distributions
df[["T_min", "T_max", "pluie_mm", "eau_mm"]].hist(figsize=(12, 8))
plt.savefig("data/processed/distributions.png")

# Corrélations
plt.figure(figsize=(12, 8))
sns.heatmap(df.select_dtypes(include="number").corr(), annot=True, fmt=".2f")
plt.savefig("data/processed/correlations.png")

# Stats par plante
print(df.groupby("type_plante")["eau_mm"].describe())